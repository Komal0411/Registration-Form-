-- 1️⃣ Create Database
CREATE DATABASE StudentDB;
GO

USE StudentDB;
GO

-- 2️⃣ If table exists, remove it safely
IF OBJECT_ID('Students', 'U') IS NOT NULL
    DROP TABLE Students;
GO

DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS AdminLogin;
-- 3️⃣ Create Proper Table
CREATE TABLE Students (
    ID INT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,   -- Unique email
    Course VARCHAR(50) NOT NULL,
    Date DATETIME DEFAULT GETDATE()       -- Automatic date
);
GO

-- 4️⃣ Admin Table for Login (Best Practice)
IF OBJECT_ID('AdminLogin', 'U') IS NOT NULL
    DROP TABLE AdminLogin;
GO

CREATE TABLE AdminLogin (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    PasswordHash VARCHAR(256) NOT NULL
);
GO

select * from AdminLogin;

-- 5️⃣ Sample Admin Insert (Password should be hashed in real apps)
-- Secure password using HASHING (SHA2)
INSERT INTO AdminLogin (Username, PasswordHash)
VALUES ('komal', 'komal123');


-- 6️⃣ Show Structure of Table
SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Students';
GO

-- 7️⃣ Select All Students
SELECT * FROM Students;
GO

-- 8️⃣ Count Records

SELECT COUNT(*) AS TotalStudents FROM Students;
GO

-- 9️⃣ Sorting Queries
SELECT * FROM Students ORDER BY Date DESC; -- Latest First
SELECT * FROM Students ORDER BY Date ASC;  -- Oldest First
GO

-- 🔟 Course-wise Statistics (Used in Chart)
SELECT Course, COUNT(*) AS TotalStudents
FROM Students
GROUP BY Course;
GO

--1️⃣1️⃣ Safe Delete Options
DELETE FROM Students;    -- Deletes data but keeps ID auto increment
TRUNCATE TABLE Students; -- Deletes data + resets ID to 1
GO
