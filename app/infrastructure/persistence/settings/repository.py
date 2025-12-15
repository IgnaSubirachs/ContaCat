from sqlalchemy.orm import Session
from typing import Optional
from app.domain.settings.entities import CompanySettings
from app.infrastructure.persistence.settings.models import CompanySettingsModel

class SqlAlchemyCompanySettingsRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get(self) -> Optional[CompanySettings]:
        with self.session_factory() as session:
            model = session.query(CompanySettingsModel).first()
            if not model:
                return None
            return self._to_entity(model)

    def save(self, settings: CompanySettings) -> None:
        with self.session_factory() as session:
            # Check if exists (singleton)
            existing = session.query(CompanySettingsModel).first()
            if existing:
                # Update ID to match existing to ensure update happens on same row
                settings.id = existing.id 
                model = self._to_model(settings)
                session.merge(model)
            else:
                model = self._to_model(settings)
                session.add(model)
            session.commit()

    def _to_entity(self, model: CompanySettingsModel) -> CompanySettings:
        return CompanySettings(
            id=model.id,
            name=model.name,
            tax_id=model.tax_id,
            address_street=model.address_street,
            address_city=model.address_city,
            address_zip=model.address_zip,
            address_province=model.address_province,
            address_country=model.address_country,
            email=model.email,
            phone=model.phone,
            website=model.website,
            logo_url=model.logo_url,
            currency=model.currency
        )

    def _to_model(self, entity: CompanySettings) -> CompanySettingsModel:
        return CompanySettingsModel(
            id=entity.id,
            name=entity.name,
            tax_id=entity.tax_id,
            address_street=entity.address_street,
            address_city=entity.address_city,
            address_zip=entity.address_zip,
            address_province=entity.address_province,
            address_country=entity.address_country,
            email=entity.email,
            phone=entity.phone,
            website=entity.website,
            logo_url=entity.logo_url,
            currency=entity.currency
        )
