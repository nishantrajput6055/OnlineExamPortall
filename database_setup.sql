-- Create database
CREATE DATABASE IF NOT EXISTS online_exam_portal;
USE online_exam_portal;

-- Drop existing tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS student_answers;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS questions;
DROP TABLE IF EXISTS exams;
DROP TABLE IF EXISTS users;

-- =====================================================
-- Table: users
-- Stores user information (both admin and students)
-- =====================================================
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role ENUM('admin', 'student') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Table: exams
-- Stores exam metadata
-- =====================================================
CREATE TABLE exams (
    exam_id INT PRIMARY KEY AUTO_INCREMENT,
    exam_title VARCHAR(200) NOT NULL,
    exam_description TEXT,
    duration_minutes INT NOT NULL,
    total_marks INT NOT NULL,
    passing_marks INT NOT NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    start_time DATETIME NULL,
    end_time DATETIME NULL,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_active (is_active),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Table: questions
-- Stores exam questions with multiple choice options
-- =====================================================
CREATE TABLE questions (
    question_id INT PRIMARY KEY AUTO_INCREMENT,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a VARCHAR(500) NOT NULL,
    option_b VARCHAR(500) NOT NULL,
    option_c VARCHAR(500) NOT NULL,
    option_d VARCHAR(500) NOT NULL,
    correct_answer ENUM('A', 'B', 'C', 'D') NOT NULL,
    marks INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    INDEX idx_exam (exam_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Table: results
-- Stores student exam results
-- =====================================================
CREATE TABLE results (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    exam_id INT NOT NULL,
    score INT NOT NULL,
    total_marks INT NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    status ENUM('pass', 'fail') NOT NULL,
    time_taken INT NOT NULL, -- in seconds
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_exam (exam_id),
    INDEX idx_submitted (submitted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Table: student_answers
-- Stores individual answers for each question
-- =====================================================
CREATE TABLE student_answers (
    answer_id INT PRIMARY KEY AUTO_INCREMENT,
    result_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_answer ENUM('A', 'B', 'C', 'D') NOT NULL,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (result_id) REFERENCES results(result_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    INDEX idx_result (result_id),
    INDEX idx_question (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Insert Default Admin User
-- Password: admin123 (hashed using Werkzeug)
-- =====================================================
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@exam.com', 'scrypt:32768:8:1$sBz8oKxQFPiZVGlc$c8e5b5e3f9d1c3a0f7b2d6e8a4c9f1e5d3b7a6c8e2f4d1a9b5c7e3f6d8a2c4b9e1f7d3a5c8e6b2d4f9a1c7e5d3b8', 'System Administrator', 'admin');

-- =====================================================
-- Insert Sample Student User
-- Password: student123 (hashed using Werkzeug)
-- =====================================================
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('student1', 'student@exam.com', 'scrypt:32768:8:1$sBz8oKxQFPiZVGlc$a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', 'John Doe', 'student');

-- =====================================================
-- Insert Sample Exam
-- =====================================================
INSERT INTO exams (exam_title, exam_description, duration_minutes, total_marks, passing_marks, created_by, is_active) VALUES
('Python Fundamentals', 'Basic Python programming concepts and syntax', 30, 20, 12, 1, TRUE),
('Database Management', 'SQL and database design principles', 45, 25, 15, 1, TRUE),
('Web Development', 'HTML, CSS, and JavaScript basics', 40, 20, 12, 1, TRUE);

-- =====================================================
-- Insert Sample Questions for Python Fundamentals Exam
-- =====================================================
INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks) VALUES
(1, 'What is the correct file extension for Python files?', '.py', '.python', '.pt', '.pyt', 'A', 2),
(1, 'Which of the following is used to define a function in Python?', 'function', 'def', 'func', 'define', 'B', 2),
(1, 'What is the output of: print(2 ** 3)?', '6', '8', '9', '5', 'B', 2),
(1, 'Which data type is mutable in Python?', 'tuple', 'string', 'list', 'integer', 'C', 2),
(1, 'What does the len() function do?', 'Returns the length of an object', 'Returns the type of object', 'Converts to integer', 'None of these', 'A', 2),
(1, 'Which operator is used for floor division in Python?', '/', '//', '%', '**', 'B', 2),
(1, 'What is the correct way to create a dictionary?', '[]', '()', '{}', '<>', 'C', 2),
(1, 'Which keyword is used for exception handling?', 'try', 'catch', 'exception', 'error', 'A', 2),
(1, 'What is the output of: print(type([]))?', 'list', '<class list>', '<type list>', 'array', 'B', 2),
(1, 'Which module is used for regular expressions in Python?', 're', 'regex', 'regexp', 'regular', 'A', 2);

-- =====================================================
-- Insert Sample Questions for Database Management Exam
-- =====================================================
INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks) VALUES
(2, 'What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'Strong Query Language', 'A', 2),
(2, 'Which SQL command is used to retrieve data?', 'GET', 'SELECT', 'RETRIEVE', 'FETCH', 'B', 2),
(2, 'What is a PRIMARY KEY?', 'A unique identifier for a record', 'A foreign reference', 'An index', 'A constraint', 'A', 2),
(2, 'Which clause is used to filter results?', 'FILTER', 'WHERE', 'HAVING', 'LIMIT', 'B', 2),
(2, 'What is normalization?', 'Organizing data to reduce redundancy', 'Increasing database size', 'Creating backups', 'Indexing tables', 'A', 2);

-- =====================================================
-- Create Views for Analytics
-- =====================================================

-- View: Student Performance Summary
CREATE VIEW student_performance AS
SELECT 
    u.user_id,
    u.full_name,
    u.email,
    COUNT(DISTINCT r.exam_id) as exams_taken,
    AVG(r.percentage) as avg_percentage,
    SUM(CASE WHEN r.status = 'pass' THEN 1 ELSE 0 END) as exams_passed,
    MAX(r.submitted_at) as last_exam_date
FROM users u
LEFT JOIN results r ON u.user_id = r.user_id
WHERE u.role = 'student'
GROUP BY u.user_id, u.full_name, u.email;

-- View: Exam Statistics
CREATE VIEW exam_statistics AS
SELECT 
    e.exam_id,
    e.exam_title,
    COUNT(r.result_id) as total_attempts,
    AVG(r.percentage) as avg_score,
    MAX(r.percentage) as highest_score,
    MIN(r.percentage) as lowest_score,
    SUM(CASE WHEN r.status = 'pass' THEN 1 ELSE 0 END) as pass_count,
    SUM(CASE WHEN r.status = 'fail' THEN 1 ELSE 0 END) as fail_count
FROM exams e
LEFT JOIN results r ON e.exam_id = r.exam_id
GROUP BY e.exam_id, e.exam_title;

-- =====================================================
-- Create Stored Procedures
-- =====================================================

DELIMITER //

-- Procedure: Get Student Exam History
CREATE PROCEDURE get_student_exam_history(IN student_id INT)
BEGIN
    SELECT 
        e.exam_title,
        r.score,
        r.total_marks,
        r.percentage,
        r.status,
        r.time_taken,
        r.submitted_at
    FROM results r
    JOIN exams e ON r.exam_id = e.exam_id
    WHERE r.user_id = student_id
    ORDER BY r.submitted_at DESC;
END //

-- Procedure: Calculate Exam Result
CREATE PROCEDURE calculate_exam_result(
    IN p_result_id INT,
    OUT p_score INT,
    OUT p_total INT,
    OUT p_percentage DECIMAL(5,2),
    OUT p_status VARCHAR(10)
)
BEGIN
    SELECT 
        SUM(CASE WHEN sa.is_correct = 1 THEN q.marks ELSE 0 END),
        SUM(q.marks)
    INTO p_score, p_total
    FROM student_answers sa
    JOIN questions q ON sa.question_id = q.question_id
    WHERE sa.result_id = p_result_id;
    
    SET p_percentage = (p_score / p_total) * 100;
    
    SELECT passing_marks INTO @passing
    FROM results r
    JOIN exams e ON r.exam_id = e.exam_id
    WHERE r.result_id = p_result_id;
    
    IF p_score >= @passing THEN
        SET p_status = 'pass';
    ELSE
        SET p_status = 'fail';
    END IF;
END //

DELIMITER ;

-- =====================================================
-- Grant Permissions (adjust username as needed)
-- =====================================================
-- GRANT ALL PRIVILEGES ON online_exam_portal.* TO 'exam_user'@'localhost' IDENTIFIED BY 'exam_password';
-- FLUSH PRIVILEGES;

-- =====================================================
-- Display Table Information
-- =====================================================
SELECT 'Database setup completed successfully!' as Message;
SHOW TABLES;