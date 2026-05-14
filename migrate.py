from app.db.session import engine
from sqlalchemy import text

sql = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_first_login BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_delete_blog BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_post_job BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_access_contact BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS can_access_consulting BOOLEAN DEFAULT FALSE;
"""

with engine.connect() as conn:
    for statement in sql.strip().split(";"):
        statement = statement.strip()
        if statement:
            conn.execute(text(statement))
    conn.commit()

print("Migration completed successfully.")
