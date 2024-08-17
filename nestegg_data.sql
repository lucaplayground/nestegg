CREATE DATABASE nestegg_data CHARACTER SET utf8;
USE nestegg_data;

-- Create Users Table
CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    currency_code VARCHAR(10) NOT NULL  -- Store currency code (e.g., USD, EUR)
);

-- Create Portfolios Table
CREATE TABLE Portfolios (
    portfolio_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    portfolio_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE -- Cascade deletion of user
);

-- Create Assets Table
CREATE TABLE Assets (
    asset_id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL UNIQUE,  -- Fund code fetched from Yahoo Finance
    name VARCHAR(100) NOT NULL,  -- Asset name fetched from Yahoo Finance
    currency_code VARCHAR(10) NOT NULL CHECK (currency_code IN ('USD', 'NZD', 'AUD', 'JPY', 'CNY', 'GBP', 'EUR', 'CAD', 'SGD'))  -- Supported currencies
);

-- Create Portfolio_Assets Table (Bridge Table)
CREATE TABLE Portfolio_Assets (
    portfolio_asset_id INT PRIMARY KEY AUTO_INCREMENT,
    portfolio_id INT NOT NULL,
    asset_id INT NOT NULL,
    position DECIMAL(10, 2),
    cost_basis DECIMAL(15, 2),
    targeted_ratio DECIMAL(5, 2),
    FOREIGN KEY (portfolio_id) REFERENCES Portfolios(portfolio_id) ON DELETE CASCADE,  -- Cascade deletion of portfolio
    FOREIGN KEY (asset_id) REFERENCES Assets(asset_id) ON DELETE CASCADE  -- Cascade deletion of asset
);

-- Add Indices
CREATE INDEX idx_user_id ON Portfolios(user_id);
CREATE INDEX idx_asset_id ON Portfolio_Assets(asset_id);