-- Create a test database
CREATE DATABASE dbtest
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

USE dbtest;

-- Create location table
CREATE TABLE location (
  location_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Create company table with FK to location (1:n)
CREATE TABLE company (
  company_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  location_id INT NOT NULL,
  FOREIGN KEY (location_id) REFERENCES location(location_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
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

-- Create teams table
CREATE TABLE teams (
  team_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Create n:m relation table between teams and employees
CREATE TABLE team_has_employee (
  team_id INT NOT NULL,
  employee_id INT NOT NULL,
  PRIMARY KEY (team_id, employee_id),
  FOREIGN KEY (team_id) REFERENCES teams(team_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Insert sample locations
INSERT INTO location (name) VALUES
('Berlin'),
('Taipei'),
('Munich');

-- Insert sample companies
INSERT INTO company (name, location_id) VALUES
('TechCorp', 1),
('DesignStudio', 2),
('HealthPlus', 3);

-- Insert sample employees
INSERT INTO employees (company_id, name, email) VALUES
(1, 'Alice Müller', 'alice.mueller@techcorp.com'),
(1, 'Bob Schneider', 'bob.schneider@techcorp.com'),
(2, 'Chen Wei', 'chen.wei@designstudio.tw'),
(2, 'Lin Mei', 'lin.mei@designstudio.tw'),
(3, 'Olga Idelevich', 'olga.idelevich@healthplus.de');

-- Insert sample teams
INSERT INTO teams (name) VALUES
('Sales'),
('Operations'),
('Finance');

-- Insert sample n:m assignments (employees can be in multiple teams)
INSERT INTO team_has_employee (team_id, employee_id) VALUES
(1, 1),
(1, 2),
(2, 2),
(2, 3),
(3, 1),
(3, 5);