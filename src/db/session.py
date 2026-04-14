import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sff.db")
IS_SQLITE = DATABASE_URL.startswith("sqlite")

engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False} if IS_SQLITE else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db() -> None:
	# Imported here to avoid circular import issues.
	from src.models.log_model import Log  # noqa: F401
	from src.models.user_model import User  # noqa: F401

	Base.metadata.create_all(bind=engine)
