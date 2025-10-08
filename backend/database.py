from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite file will be created next to the backend folder
DATABASE_URL = "sqlite:///./test.db"

# For sqlite we need check_same_thread False when using from different threads
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
	"""Yields a database session and ensures it's closed after use.

	Use in FastAPI dependencies as: Depends(get_db)
	"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db():
	"""Create database tables."""
	Base.metadata.create_all(bind=engine)