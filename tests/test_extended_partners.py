import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.partners.services import PartnerService
from app.infrastructure.db.base import Base
from app.infrastructure.persistence.partners.models import PartnerModel
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository


class ExtendedPartnerTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(engine, tables=[PartnerModel.__table__])
        self.service = PartnerService(
            SqlAlchemyPartnerRepository(sessionmaker(bind=engine))
        )

    def test_extended_partner_fields_round_trip(self):
        partner = self.service.create_partner(
            name="Client complet SL",
            tax_id="12345678Z",
            email="info@example.com",
            phone="930000000",
            is_customer=True,
            is_supplier=True,
            relationship_since=date(2026, 1, 1),
            swift_bic="CAIXESBBXXX",
            credit_limit=12000,
            payment_day=15,
            contract_summary="Contracte anual",
            accrual_notes="Periodificació mensual",
        )

        stored = self.service.get_partner_by_id(partner.id)

        self.assertEqual(stored.swift_bic, "CAIXESBBXXX")
        self.assertEqual(stored.payment_day, 15)
        self.assertEqual(stored.credit_limit, 12000)
        self.assertEqual(stored.contract_summary, "Contracte anual")
        self.assertEqual(stored.accrual_notes, "Periodificació mensual")
        self.assertEqual(stored.relationship_since, date(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
