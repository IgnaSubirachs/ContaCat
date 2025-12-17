-- Migration: Add email support and password reset functionality
-- Date: 2025-12-17

-- Add email field to users table
ALTER TABLE users 
ADD COLUMN email VARCHAR(255) UNIQUE AFTER username,
ADD INDEX idx_email (email);

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_expires (expires_at),
    INDEX idx_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add default emails to existing users (can be updated later)
UPDATE users SET email = CONCAT(username, '@contacat.local') WHERE email IS NULL;
