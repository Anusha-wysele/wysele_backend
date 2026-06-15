from app.db.session import engine
from sqlalchemy import text

sql = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_first_login BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_delete_blog BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_post_job BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_access_contact BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_access_consulting BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR;
ALTER TABLE users ADD COLUMN IF NOT EXISTS company_name VARCHAR;

ALTER TABLE jobs ADD COLUMN IF NOT EXISTS company_id VARCHAR;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS company_name VARCHAR;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS title VARCHAR NOT NULL DEFAULT 'Job Title';
ALTER TABLE blogs ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'ACTIVE';
ALTER TABLE blogs ADD COLUMN IF NOT EXISTS image_urls JSON DEFAULT '[]'::json;

ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS email VARCHAR;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS details JSON;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS ip_address VARCHAR;

CREATE TABLE IF NOT EXISTS user_tokens (
    token VARCHAR PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_type VARCHAR NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_tokens_token ON user_tokens(token);

"""

with engine.connect() as conn:
    for statement in sql.strip().split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))
    conn.commit()

print("Migration completed successfully.")
