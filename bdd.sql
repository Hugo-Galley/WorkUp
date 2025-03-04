CREATE TABLE Jobs(
    IdJobs INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Title TEXT,
    Salary VARCHAR(100),
    Entreprise VARCHAR(100),
    Link VARCHAR(255),
    Localisation VARCHAR(50),
    Source VARCHAR(255),
    Description TEXT
)