-- Create a test database
CREATE DATABASE testdb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE testdb;

-- Create company table
CREATE TABLE company (
  company_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  location VARCHAR(100)
) ENGINE=InnoDB;

-- Create employees table with FK to company
CREATE TABLE employees (
  employee_id INT AUTO_INCREMENT PRIMARY KEY,
  company_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE,
  FOREIGN KEY (company_id) REFERENCES company(company_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Insert sample companies
INSERT INTO company (name, location) VALUES
('TechCorp', 'Berlin'),
('DesignStudio', 'Taipei'),
('HealthPlus', 'Munich');

-- Insert sample employees
INSERT INTO employees (company_id, name, email) VALUES
(1, 'Alice Müller', 'alice.mueller@techcorp.com'),
(1, 'Bob Schneider', 'bob.schneider@techcorp.com'),
(2, 'Chen Wei', 'chen.wei@designstudio.tw'),
(2, 'Lin Mei', 'lin.mei@designstudio.tw'),
(3, 'Olga Idelevich', 'olga.idelevich@healthplus.de');