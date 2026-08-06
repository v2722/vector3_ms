-- ============================================================
-- Migration: add user ownership to portfolios
-- Run this once against an EXISTING database that was created
-- before the user table existed. New installs can just run
-- init_db.sql.
-- ============================================================

USE portfolio_manager;

-- Create the user table (one user can own multiple portfolios)
CREATE TABLE IF NOT EXISTS user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add the ownership column to portfolio
SET @col_exists = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'portfolio'
      AND COLUMN_NAME = 'user_id'
);
SET @ddl = IF(@col_exists = 0,
    'ALTER TABLE portfolio ADD COLUMN user_id INT NULL',
    'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Link portfolio to user
ALTER TABLE portfolio
    ADD CONSTRAINT fk_portfolio_user
    FOREIGN KEY (user_id) REFERENCES user(user_id)
    ON DELETE SET NULL;
