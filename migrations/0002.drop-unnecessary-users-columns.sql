ALTER TABLE users
    DROP COLUMN reset_password_token,
    DROP COLUMN reset_password_sent_at,
    DROP COLUMN allow_password_change,
    DROP COLUMN remember_created_at,
    DROP COLUMN confirmation_token,
    DROP COLUMN confirmation_sent_at,
    DROP COLUMN tokens;
