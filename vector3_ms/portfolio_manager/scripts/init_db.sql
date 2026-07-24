-- ============================================================
-- Portfolio Manager Database Schema (MySQL)
-- Upgraded with ERD features
-- ============================================================

CREATE DATABASE IF NOT EXISTS portfolio_manager;
USE portfolio_manager;

-- ============================================================
-- PORTFOLIO TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- ASSET TYPE TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_type (
    asset_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT
);

-- ============================================================
-- ASSET TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS asset (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200),
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    asset_type_id INT,

    FOREIGN KEY (asset_type_id)
        REFERENCES asset_type(asset_type_id)
        ON DELETE SET NULL
);

-- ============================================================
-- PORTFOLIO ITEM TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS portfolio_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    asset_id INT NOT NULL,
    quantity DECIMAL(18,4) NOT NULL,
    avg_buy_price DECIMAL(18,4) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (portfolio_id)
        REFERENCES portfolio(portfolio_id)
        ON DELETE CASCADE,

    FOREIGN KEY (asset_id)
        REFERENCES asset(asset_id)
        ON DELETE CASCADE
);

-- ============================================================
-- PRICE HISTORY TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS price_history (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(18,4),
    high DECIMAL(18,4),
    low DECIMAL(18,4),
    close DECIMAL(18,4),
    volume BIGINT,
    source VARCHAR(50) DEFAULT 'Yahoo Finance',

    UNIQUE(asset_id, date),

    FOREIGN KEY (asset_id)
        REFERENCES asset(asset_id)
        ON DELETE CASCADE
);

-- ============================================================
-- TRANSACTION TABLE (ORIGINAL)
-- ============================================================
CREATE TABLE IF NOT EXISTS transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    asset_id INT NOT NULL,
    type ENUM('BUY','SELL') NOT NULL,
    quantity DECIMAL(18,4) NOT NULL,
    price DECIMAL(18,4) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (portfolio_id)
        REFERENCES portfolio(portfolio_id)
        ON DELETE CASCADE,

    FOREIGN KEY (asset_id)
        REFERENCES asset(asset_id)
        ON DELETE CASCADE
);

-- ============================================================
-- ASSET TRANSACTION TABLE (NEW - ERD)
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    transaction_type ENUM('BUY','SELL','DIVIDEND') NOT NULL,
    quantity DECIMAL(18,4),
    price DECIMAL(18,4),
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    FOREIGN KEY (asset_id)
        REFERENCES asset(asset_id)
        ON DELETE CASCADE
);

-- ============================================================
-- PORTFOLIO PERFORMANCE TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS portfolio_performance (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    date DATE NOT NULL,
    total_value DECIMAL(18,4),
    daily_change DECIMAL(18,4),
    daily_change_percent DECIMAL(6,2),
    notes TEXT,

    FOREIGN KEY (portfolio_id)
        REFERENCES portfolio(portfolio_id)
        ON DELETE CASCADE
);

-- ============================================================
-- MARKET DATA CACHE TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS market_data_cache (
    cache_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    json_payload LONGTEXT
);

-- ============================================================
-- EXTERNAL API REQUEST LOG TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS external_api_request (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20),
    request_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_time DATETIME,
    status VARCHAR(50),
    payload LONGTEXT
);

-- ============================================================
-- AUDIT LOG TABLE (NEW)
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_name VARCHAR(100),
    entity_id INT,
    action VARCHAR(50),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);
