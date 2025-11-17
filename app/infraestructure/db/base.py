from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
import os


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    # Pots sobreescriure-ho amb una variable d'entorn
    return os.getenv("DATABASE_URL", "sqlite:///./accounting.db")


engine = create_engine(
    get_database_url(),
    echo=False,
    future=True,
)

SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db():
    """Create all tables."""
    from app.infrastructure.accounts.sqlalchemy_models import AccountModel
    Base.metadata.create_all(bind=engine)
