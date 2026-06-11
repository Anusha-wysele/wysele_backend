from app.db.session import engine
from sqlalchemy import text

indexes = [
    # Enable pg_trgm extension
    "CREATE EXTENSION IF NOT EXISTS pg_trgm",

    # Jobs — trigram GIN indexes for optimized text search
    "CREATE INDEX IF NOT EXISTS idx_jobs_title_trgm ON jobs USING gin (job_title gin_trgm_ops)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_role_trgm ON jobs USING gin (role gin_trgm_ops)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_location_trgm ON jobs USING gin (location gin_trgm_ops)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_dept_trgm ON jobs USING gin (department gin_trgm_ops)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_workmode_trgm ON jobs USING gin (work_mode gin_trgm_ops)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_desc_trgm ON jobs USING gin (description gin_trgm_ops)",

    # Jobs — standard B-Tree indexes
    "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_is_deleted ON jobs(is_deleted)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_posted_by ON jobs(posted_by)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_deadline ON jobs(application_deadline)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_role ON jobs(role)",
    "CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location)",

    # Applications
    "CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id)",
    "CREATE INDEX IF NOT EXISTS idx_applications_email ON applications(email)",

    # Blogs
    "CREATE INDEX IF NOT EXISTS idx_blogs_category ON blogs(category)",
    "CREATE INDEX IF NOT EXISTS idx_blogs_created_at ON blogs(created_at DESC)",

    # Contact
    "CREATE INDEX IF NOT EXISTS idx_contact_created_at ON contact_inquiries(created_at DESC)",

    # Consulting
    "CREATE INDEX IF NOT EXISTS idx_consulting_email ON consulting_inquiries(email)",
    "CREATE INDEX IF NOT EXISTS idx_consulting_created_at ON consulting_inquiries(created_at DESC)",

    # Users
    "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
    "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
]

with engine.connect() as conn:
    for idx in indexes:
        conn.execute(text(idx))
    conn.commit()

print(f"{len(indexes)} indexes created successfully.")
