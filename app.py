import hashlib
from flask import Flask, render_template, request, redirect, send_file, session, url_for
import pyodbc
import pandas as pd
from reportlab.pdfgen import canvas
from flask_mail import Mail, Message
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "admin@123"

#SQL CONNECTION SETUP
conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=BXNSXL\\SQLEXPRESS;"
    "Database=StudentDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

#EMAIL CONFIG
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'komalbansal2811@gmail.com'
app.config['MAIL_PASSWORD'] = 'komal12345'
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)

#HOME PAGE
@app.route('/')
def index():
    return render_template("index.html")

#ADD STUDENT
@app.route('/add', methods=['POST'])
def add():

    try:
        ID = request.form['id']
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        # CHECK if ID already exists
        cursor.execute("SELECT COUNT(*) FROM Students WHERE ID=?", ID)
        existing = cursor.fetchone()[0]

        if existing > 0:
            return "⚠️ ID already exists! Please enter a new one."

        cursor.execute("INSERT INTO Students (ID, Name, Email, Course) VALUES (?, ?, ?, ?)",
                       ID, name, email, course)
        conn.commit()
        return render_template("success.html", name=name)

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ---------------- LOGIN (ADMIN) -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM AdminLogin WHERE Username=?", (username,))
        user = cursor.fetchone()

        if user and user[2] == password:  # user[2] = PasswordHash column
            session['user'] = username
            return redirect('/view')
        else:
            error = "Invalid Username or Password!"

    return render_template("login.html", error=error)


# ---------------- VIEW STUDENTS -------------------
@app.route('/view')
def view():
    if 'user' not in session:
        return redirect('/login')
    try:
        cursor.execute("SELECT * FROM Students ORDER BY Date DESC")
        data = cursor.fetchall()
    except Exception as e:
        print(e)
        data = []
    return render_template("view.html", students=data)


# ---------------- EDIT STUDENT -------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        cursor.execute("UPDATE Students SET Name=?, Email=?, Course=? WHERE ID=?", name, email, course, id)
        conn.commit()
        return redirect('/view')

    cursor.execute("SELECT * FROM Students WHERE ID=?", id)
    student = cursor.fetchone()
    return render_template("edit.html", student=student)

# ---------------- DELETE STUDENT -----------------
@app.route('/delete/<int:id>')
def delete_student(id):
    if 'user' not in session:
        return redirect('/login')
    cursor.execute("DELETE FROM Students WHERE ID=?", id)
    conn.commit()
    return redirect('/view')

@app.route('/delete_all')
def delete_all():
    if 'user' not in session:
        return redirect('/login')
    cursor.execute("DELETE FROM Students")
    conn.commit()
    return redirect('/view')

# ---------------- EXPORT EXCEL -------------------
@app.route('/export_excel')
def export_excel():
    cursor.execute("SELECT * FROM Students")
    rows = cursor.fetchall()
  
    columns = [column[0] for column in cursor.description]

    df = pd.DataFrame.from_records(rows, columns=columns)
    file_path = 'students.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)


# ---------------- EXPORT PDF ---------------------
@app.route('/export_pdf')
def export_pdf():
    cursor.execute("SELECT * FROM Students")
    rows = cursor.fetchall()
    file_path = 'students.pdf'
    c = canvas.Canvas(file_path)
    c.drawString(200, 800, "Student Details")
    y_pos = 760
    for row in rows:
        c.drawString(50, y_pos, f"ID: {row[0]} | {row[1]} | {row[2]} | {row[3]}")
        y_pos -= 20
    c.save()
    return send_file(file_path, as_attachment=True)

# ---------------- COURSE CHART -------------------
from io import BytesIO
import base64

@app.route('/chart')
def chart():
    cursor.execute("SELECT Course, COUNT(*) FROM Students GROUP BY Course")
    rows = cursor.fetchall()

    courses = [row[0] for row in rows]
    counts = [row[1] for row in rows]

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    plt.figure(figsize=(6,6))
    plt.pie(counts, labels=courses, autopct="%1.1f%%", startangle=140)
    plt.title("Students per Course")

    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()

    return render_template("chart.html", chart_data=chart_base64)


# ---------------- LOGOUT ------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- RUN ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
