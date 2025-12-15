from typing import Optional
from app.domain.settings.entities import CompanySettings
from app.infrastructure.persistence.settings.repository import SqlAlchemyCompanySettingsRepository

class SettingsService:
    def __init__(self, repository: SqlAlchemyCompanySettingsRepository):
        self._repository = repository

    def get_settings(self) -> Optional[CompanySettings]:
        """Get company settings. Returns None if not configured."""
        return self._repository.get()

    def get_settings_or_default(self) -> CompanySettings:
        """Get company settings o return a default placeholder."""
        settings = self.get_settings()
        if settings:
            return settings
        return CompanySettings(
            name="La Teva Empresa S.L.",
            tax_id="B12345678",
            address_street="C/ Exemple 123",
            address_city="Barcelona",
            address_province="Barcelona",
            address_zip="08000"
        )

    def save_settings(self, settings: CompanySettings) -> None:
        """Save company settings."""
        # Validate minimal fields
        if not settings.name:
            raise ValueError("El nom de l'empresa és obligatori.")
        if not settings.tax_id:
            raise ValueError("El NIF/CIF és obligatori.")
            
        self._repository.save(settings)
