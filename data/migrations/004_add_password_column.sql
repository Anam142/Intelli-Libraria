-- Add password column with default value
ALTER TABLE users ADD COLUMN password TEXT DEFAULT '1234';

-- Update the default password for the admin user
UPDATE users SET password = '1234' WHERE email = 'admin@lms.test';

-- Ensure the trigger exists for updating timestamps
CREATE TRIGGER IF NOT EXISTS update_users_timestamp
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
