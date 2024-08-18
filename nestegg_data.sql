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


-- Insert Test Users
INSERT INTO Users (username, email, password, salt, currency_code) 
VALUES ('user1', 'user1@example.com', 'b0eab1b9f97d8b71ce5c4c34b28687769cab857ce5ae7366a0c30030550d08db', '265238951573607fe9eaf3ab26f0f511', 'USD'),
	   ('user2', 'user2@example.com', 'd56739ed8eb8e412eaccd5923307f3c3b51e0d380ce80eaf6896ddf567382862' , '243b39bad4ddff59eec372a066fcff75', 'CNY'),
       ('user3', 'user3@example.com', 'b991ce0f0c55a5246381e7d871a80e0b7e6c7b6f3624930dffd155cab9bdb572', 'e51d14b67eb4e458a1da435dd409cc58', 'JPD');