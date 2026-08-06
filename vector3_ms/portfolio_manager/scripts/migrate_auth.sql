-- ============================================================
-- Migration: add authentication columns to the user table
-- Run this once against an EXISTING database created before the
-- login/register feature existed. New installs just run init_db.sql.
-- ============================================================

USE portfolio_manager;

SET @exists = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'user'
      AND COLUMN_NAME = 'username'
);
SET @ddl = IF(@exists = 0,
    'ALTER TABLE user ADD COLUMN username VARCHAR(100) NULL UNIQUE',
    'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @exists = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'user'
      AND COLUMN_NAME = 'password'
);
SET @ddl = IF(@exists = 0,
    'ALTER TABLE user ADD COLUMN password VARCHAR(255) NULL',
    'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @exists = (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'user'
      AND COLUMN_NAME = 'email'
);
SET @ddl = IF(@exists = 0,
    'ALTER TABLE user ADD COLUMN email VARCHAR(255) NULL',
    'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;