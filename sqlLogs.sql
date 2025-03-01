CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

ALTER TABLE Users
ADD COLUMN email VARCHAR(255) NOT NULL UNIQUE,
ADD COLUMN password VARCHAR(255) NOT NULL,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE Users
ADD COLUMN external_auth_provider VARCHAR(50),
ADD COLUMN external_auth_id VARCHAR(255),
ADD CONSTRAINT unique_external_auth UNIQUE (external_auth_provider, external_auth_id);

CREATE TABLE Projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    user_id INT,
    proj_info TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

ALTER TABLE Projects
ADD COLUMN description TEXT,
ADD COLUMN documents TEXT,
ADD COLUMN photos TEXT,
ADD COLUMN links TEXT,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

CREATE TABLE Evaluations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    proj_id INT,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50),
    FOREIGN KEY (proj_id) REFERENCES Projects(id)
);

ALTER TABLE Evaluations
MODIFY COLUMN status ENUM('START', 'IN_PORGRESS', 'COMPELTED') DEFAULT 'START';

ALTER TABLE Evaluations
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

CREATE TABLE User_agents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    eval_id INT,
    info_prompt TEXT,
    FOREIGN KEY (eval_id) REFERENCES Evaluations(id)
);

CREATE TABLE Proj_managers_Agents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    eval_id INT,
    info_prompt TEXT,
    FOREIGN KEY (eval_id) REFERENCES Evaluations(id)
);

CREATE TABLE Reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    eval_id INT,
    FOREIGN KEY (eval_id) REFERENCES Evaluations(id)
);

ALTER TABLE Projects
DROP COLUMN proj_info,
DROP COLUMN documents,
DROP COLUMN photos,
DROP COLUMN links;



CREATE TABLE DesignSources (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    type VARCHAR(50) NOT NULL,
    file_key VARCHAR(255) NOT NULL,
    access_token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

ALTER TABLE Evaluations
DROP FOREIGN KEY evaluations_ibfk_1;

ALTER TABLE Evaluations
DROP COLUMN proj_id;

ALTER TABLE Evaluations
ADD CONSTRAINT fk_evaluations_product
FOREIGN KEY (product_id) REFERENCES Products(id);

CREATE TABLE Products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT UNIQUE,
    name VARCHAR(255) NOT NULL,
    custom_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES Projects(id)
);

CREATE TABLE DesignSources (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    type VARCHAR(50) NOT NULL,
    file_key VARCHAR(255) NOT NULL,
    access_token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

CREATE TABLE DocumentationSources (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    type VARCHAR(50) NOT NULL,
    url VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

CREATE INDEX idx_product_id ON DesignSources(product_id);
CREATE INDEX idx_product_id ON DocumentationSources(product_id);
CREATE INDEX idx_product_id ON Evaluations(product_id);

-- Alter DesignSources table
ALTER TABLE DesignSources
ADD COLUMN storage_url VARCHAR(255),
ADD COLUMN file_size BIGINT,
ADD COLUMN content_type VARCHAR(100),
ADD COLUMN fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Alter DocumentationSources table
ALTER TABLE DocumentationSources
ADD COLUMN storage_url VARCHAR(255),
ADD COLUMN file_size BIGINT,
ADD COLUMN content_type VARCHAR(100),
ADD COLUMN fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE user_agents RENAME TO EvaluationUserAgents;

CREATE TABLE UserAgentDefinitions (
    id SERIAL PRIMARY KEY,
    created_by_user_id INTEGER REFERENCES Users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    characteristics json,
    is_predefined BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modify UserAgentDefinitions table
ALTER TABLE UserAgentDefinitions
MODIFY COLUMN id INT AUTO_INCREMENT;
