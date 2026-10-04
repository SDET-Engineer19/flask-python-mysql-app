-- Run once as a MySQL admin user:  mysql -u root -p < schema.sql
CREATE DATABASE IF NOT EXISTS employee_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE employee_db;

CREATE TABLE IF NOT EXISTS employees (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    employee_id   VARCHAR(20)    NOT NULL UNIQUE,
    employee_name VARCHAR(100)   NOT NULL,
    salary        DECIMAL(12, 2) NOT NULL CHECK (salary >= 0),
    designation   VARCHAR(100)   NOT NULL,
    city          VARCHAR(100)   NOT NULL,
    created_at    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Least-privilege application user (change the password!)
CREATE USER IF NOT EXISTS 'emp_app'@'localhost' IDENTIFIED BY 'change_me';
GRANT SELECT, INSERT ON employee_db.employees TO 'emp_app'@'localhost';
FLUSH PRIVILEGES;
