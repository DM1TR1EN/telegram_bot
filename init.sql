CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    language VARCHAR(2) DEFAULT 'ru',
    has_demo_access BOOLEAN DEFAULT FALSE,
    demo_access_granted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_has_demo_access ON users(has_demo_access); 