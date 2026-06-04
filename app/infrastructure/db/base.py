from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.config import APP_DEBUG, DATABASE_URL

class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=APP_DEBUG,
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
    from app.infrastructure.persistence.auth.repositories import UserModel  # noqa: F401
    from app.infrastructure.persistence.fiscal.models import FiscalYearModel  # noqa: F401
    from app.infrastructure.persistence.treasury.models import BankAccountModel  # noqa: F401
    from app.infrastructure.persistence.core.models import (  # noqa: F401
        CompanyModel,
        DocumentSequenceModel,
        ProductModel,
        TaxRateModel,
        WarehouseModel,
    )

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
