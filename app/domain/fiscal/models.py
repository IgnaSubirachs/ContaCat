from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List

@dataclass
class VatDetail:
    """Holds aggregated data for a specific VAT Rate."""
    rate: int
    base: Decimal = Decimal("0.00")
    quota: Decimal = Decimal("0.00")

    def add(self, base: Decimal, quota: Decimal):
        self.base += base
        self.quota += quota

@dataclass
class Model303Data:
    """
    Data structure for AEAT Model 303 (Auto-liquidació IVA).
    Simplification of the official model.
    """
    year: int
    period: str # 1T, 2T, 3T, 4T, 01...12
    
    # IVA Repercutit (Output VAT - Sales)
    # Keys: 4, 10, 21
    repercutit: Dict[int, VatDetail] = field(default_factory=dict)
    
    # IVA Suportat (Input VAT - Purchases)
    suportat: Dict[int, VatDetail] = field(default_factory=dict)
    
    # Totals
    total_repercutit_quota: Decimal = Decimal("0.00")
    total_suportat_quota: Decimal = Decimal("0.00")
    
    result_quota: Decimal = Decimal("0.00") # Repercutit - Suportat
    
    company_name: str = ""
    company_nif: str = ""
    
    def __post_init__(self):
        # Initialize standard rates
        for r in [4, 10, 21]:
            if r not in self.repercutit:
                self.repercutit[r] = VatDetail(rate=r)
            if r not in self.suportat:
                self.suportat[r] = VatDetail(rate=r)

    def calculate_totals(self):
        self.total_repercutit_quota = sum(d.quota for d in self.repercutit.values())
        self.total_suportat_quota = sum(d.quota for d in self.suportat.values())
        self.result_quota = self.total_repercutit_quota - self.total_suportat_quota


@dataclass
class Model111Data:
    year: int
    period: str
    
    # I. Rendiments del treball (Nomines)
    work_perceptors: int = 0
    work_base: Decimal = Decimal(0)
    work_quota: Decimal = Decimal(0)
    
    # II. Activitats economiques (Professionals)
    pro_perceptors: int = 0
    pro_base: Decimal = Decimal(0)
    pro_quota: Decimal = Decimal(0)
    
    total_quota: Decimal = Decimal(0)
    
    company_name: str = ""
    nif: str = ""

    def calculate_totals(self):
        self.total_quota = self.work_quota + self.pro_quota
