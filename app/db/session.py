from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,           # maintain 10 persistent connections
    max_overflow=20,        # allow 20 extra under load
    pool_timeout=30,        # wait max 30s for a connection
    pool_recycle=1800,      # recycle connections every 30 mins
    pool_pre_ping=False,    # skip ping — saves ~5ms per request
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,        # prevent unnecessary flushes
    bind=engine
)