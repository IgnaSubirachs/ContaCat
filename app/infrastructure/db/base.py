from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.config import DATABASE_URL  # el tens a l'arrel

class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=True,     # posa False si no vols veure els SQL per pantalla
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def init_db():
    """
    Crea totes les taules definides a models que hereten de Base.
    """
    # importa els models perquè quedin registrats a Base.metadata
    from app.infrastructure.persistence.accounts.models import AccountModel  # noqa: F401
    from app.infrastructure.persistence.partners.models import PartnerModel  # noqa: F401
    from app.infrastructure.persistence.hr.models import EmployeeModel  # noqa: F401
    from app.infrastructure.persistence.audit.models import AuditLogModel  # noqa: F401
    from app.infrastructure.persistence.documents.models import DocumentModel  # noqa: F401
    from app.infrastructure.persistence.accounting.models import AccountModel as AccAccountModel  # noqa: F401
    from app.infrastructure.persistence.accounting.models import JournalEntryModel, JournalLineModel  # noqa: F401
    from app.infrastructure.persistence.sales.models import QuoteModel, SalesOrderModel, SalesInvoiceModel, SalesLineModel  # noqa: F401
    from app.infrastructure.persistence.assets.models import AssetModel, DepreciationEntryModel  # noqa: F401
    from app.infrastructure.persistence.inventory.models import StockItemModel, StockMovementModel  # noqa: F401

    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency generator for FastAPI to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
