-- Initialize database for SamIT Global
-- This script runs automatically when MySQL container starts for the first time

-- Create database if it doesn't exist (usually already created by MYSQL_DATABASE env var)
CREATE DATABASE IF NOT EXISTS samit_global CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE samit_global;

-- Set timezone
SET time_zone = '+00:00';

-- Create indexes for better performance (tables will be created by SQLAlchemy)
-- This is just for reference, actual tables are created by the application

-- Grant privileges (if needed)
-- GRANT ALL PRIVILEGES ON samit_global.* TO 'samit_user'@'%';
-- FLUSH PRIVILEGES;

