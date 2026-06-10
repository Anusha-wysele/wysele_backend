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

ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS email VARCHAR;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS details JSON;
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS ip_address VARCHAR;
"""

with engine.connect() as conn:
    for statement in sql.strip().split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))
    conn.commit()

print("Migration completed successfully.")
