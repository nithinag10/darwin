CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL
);

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