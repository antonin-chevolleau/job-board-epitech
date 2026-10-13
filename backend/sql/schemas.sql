-- WARNING : This file delete all tables in DB
SET
  FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS job_applications,
advertisements,
users,
companies;

SET
  FOREIGN_KEY_CHECKS = 1;

CREATE TABLE
  companies (
    id INT AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_companies_name (name),
    UNIQUE KEY uq_companies_email (email)
  );

CREATE TABLE
  users (
    id INT AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role ENUM ('user', 'recruiter', 'admin') NOT NULL DEFAULT 'user',
    company_id INT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_user_name (user_name),
    UNIQUE KEY uq_users_email (email),
    CONSTRAINT fk_users_company FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE SET NULL
  );

CREATE TABLE
  advertisements (
    id INT AUTO_INCREMENT,
    company_id INT NOT NULL,
    user_id INT NULL,
    title VARCHAR(150) NOT NULL,
    short_description VARCHAR(300) NOT NULL,
    full_description TEXT NOT NULL,
    location VARCHAR(150) NULL,
    salary DECIMAL(10, 2) NULL,
    contract_type ENUM ('CDI', 'CDD', 'Stage', 'Alternance', 'Freelance') NOT NULL,
    working_time VARCHAR(50) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_advertisements_is_active (is_active),
    CONSTRAINT fk_advertisements_company FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE,
    CONSTRAINT fk_advertisements_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
  );

CREATE TABLE
  job_applications (
    id INT AUTO_INCREMENT,
    advertisement_id INT NOT NULL,
    user_id INT NULL,
    applicant_name VARCHAR(200) NOT NULL,
    applicant_email VARCHAR(255) NOT NULL,
    applicant_phone VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    status ENUM ('pending', 'reviewed', 'accepted', 'rejected') NOT NULL DEFAULT 'pending',
    email_sent_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_application (advertisement_id, applicant_email),
    CONSTRAINT fk_job_applications_advertisement FOREIGN KEY (advertisement_id) REFERENCES advertisements (id) ON DELETE CASCADE,
    CONSTRAINT fk_job_applications_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
  );