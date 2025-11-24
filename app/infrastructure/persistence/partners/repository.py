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
            model = self._entity_to_model(partner)
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
            return [self._model_to_entity(m) for m in models]
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
            return self._model_to_entity(model)
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
            return self._model_to_entity(model)
        finally:
            session.close()
    
    def update(self, partner: Partner) -> None:
        session: Session = self._session_factory()
        try:
            stmt = select(PartnerModel).where(PartnerModel.id == partner.id)
            result = session.execute(stmt)
            model: PartnerModel | None = result.scalars().first()
            
            if not model:
                raise ValueError(f"No s'ha trobat el partner amb ID {partner.id}")
            
            # Update all fields
            model.name = partner.name
            model.email = partner.email
            model.phone = partner.phone
            model.is_supplier = partner.is_supplier
            model.is_customer = partner.is_customer
            model.document_type = partner.document_type
            model.address_street = partner.address_street
            model.address_number = partner.address_number
            model.address_floor = partner.address_floor
            model.postal_code = partner.postal_code
            model.city = partner.city
            model.province = partner.province
            model.country = partner.country
            model.vat_regime = partner.vat_regime
            model.is_intra_eu = partner.is_intra_eu
            model.eu_vat_number = partner.eu_vat_number
            model.iban = partner.iban
            model.payment_method = partner.payment_method
            model.payment_days = partner.payment_days
            
            session.commit()
        finally:
            session.close()
    
    def delete(self, partner_id: str) -> None:
        session: Session = self._session_factory()
        try:
            stmt = select(PartnerModel).where(PartnerModel.id == partner_id)
            result = session.execute(stmt)
            model: PartnerModel | None = result.scalars().first()
            
            if not model:
                raise ValueError(f"No s'ha trobat el partner amb ID {partner_id}")
            
            session.delete(model)
            session.commit()
        finally:
            session.close()
    
    def _model_to_entity(self, model: PartnerModel) -> Partner:
        """Convert SQLAlchemy model to domain entity."""
        return Partner(
            id=model.id,
            name=model.name,
            tax_id=model.tax_id,
            email=model.email,
            phone=model.phone,
            is_supplier=model.is_supplier,
            is_customer=model.is_customer,
            document_type=model.document_type,
            address_street=model.address_street,
            address_number=model.address_number,
            address_floor=model.address_floor,
            postal_code=model.postal_code,
            city=model.city,
            province=model.province,
            country=model.country,
            vat_regime=model.vat_regime,
            is_intra_eu=model.is_intra_eu,
            eu_vat_number=model.eu_vat_number,
            iban=model.iban,
            payment_method=model.payment_method,
            payment_days=model.payment_days,
        )
    
    def _entity_to_model(self, partner: Partner) -> PartnerModel:
        """Convert domain entity to SQLAlchemy model."""
        return PartnerModel(
            id=partner.id,
            name=partner.name,
            tax_id=partner.tax_id,
            email=partner.email,
            phone=partner.phone,
            is_supplier=partner.is_supplier,
            is_customer=partner.is_customer,
            document_type=partner.document_type,
            address_street=partner.address_street,
            address_number=partner.address_number,
            address_floor=partner.address_floor,
            postal_code=partner.postal_code,
            city=partner.city,
            province=partner.province,
            country=partner.country,
            vat_regime=partner.vat_regime,
            is_intra_eu=partner.is_intra_eu,
            eu_vat_number=partner.eu_vat_number,
            iban=partner.iban,
            payment_method=partner.payment_method,
            payment_days=partner.payment_days,
        )
