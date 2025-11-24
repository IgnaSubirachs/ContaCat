from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.partners.entities import Partner
from app.domain.partners.repositories import PartnerRepository
from app.infrastructure.persistence.partners.models import PartnerModel
from app.infrastructure.db.base import SessionLocal


class SqlAlchemyPartnerRepository(PartnerRepository):
    """SQLAlchemy-based implementation of PartnerRepository."""

    def __init__(self, session_factory=SessionLocal):
        self._session_factory = session_factory

    def add(self, partner: Partner) -> None:
        session: Session = self._session_factory()
        try:
            model = PartnerModel(
                id=partner.id,
                name=partner.name,
                tax_id=partner.tax_id,
                email=partner.email,
                phone=partner.phone,
                is_supplier=partner.is_supplier,
                is_customer=partner.is_customer,
            )
            session.add(model)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError(f"Ja existeix un partner amb el NIF/CIF {partner.tax_id}")
        finally:
            session.close()

    def list_all(self) -> List[Partner]:
        session: Session = self._session_factory()
        try:
            stmt = select(PartnerModel).order_by(PartnerModel.name)
            result = session.execute(stmt)
            models: List[PartnerModel] = result.scalars().all()

            return [
                Partner(
                    id=m.id,
                    name=m.name,
                    tax_id=m.tax_id,
                    email=m.email,
                    phone=m.phone,
                    is_supplier=m.is_supplier,
                    is_customer=m.is_customer,
                )
                for m in models
            ]
        finally:
            session.close()

    def find_by_id(self, partner_id: str) -> Optional[Partner]:
        session: Session = self._session_factory()
        try:
            stmt = select(PartnerModel).where(PartnerModel.id == partner_id)
            result = session.execute(stmt)
            model: PartnerModel | None = result.scalars().first()
            if not model:
                return None
            return Partner(
                id=model.id,
                name=model.name,
                tax_id=model.tax_id,
                email=model.email,
                phone=model.phone,
                is_supplier=model.is_supplier,
                is_customer=model.is_customer,
            )
        finally:
            session.close()

    def find_by_tax_id(self, tax_id: str) -> Optional[Partner]:
        session: Session = self._session_factory()
        try:
            stmt = select(PartnerModel).where(PartnerModel.tax_id == tax_id)
            result = session.execute(stmt)
            model: PartnerModel | None = result.scalars().first()
            if not model:
                return None
            return Partner(
                id=model.id,
                name=model.name,
                tax_id=model.tax_id,
                email=model.email,
                phone=model.phone,
                is_supplier=model.is_supplier,
                is_customer=model.is_customer,
            )
        finally:
            session.close()
