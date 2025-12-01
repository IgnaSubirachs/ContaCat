"""
Calculadora de cotitzacions a la Seguretat Social segons taules oficials 2024.
Inclou grups de cotització, bases mínimes/màximes i percentatges.
"""
from decimal import Decimal
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class SocialSecurityGroup:
    """
    Grup de cotització a la Seguretat Social.
    Grups 1-11 segons classificació oficial.
    """
    group_number: int
    name: str
    min_base: Decimal  # Base mínima mensual
    max_base: Decimal  # Base màxima mensual
    
    # Percentatges de cotització (sobre base de cotització)
    # Contingències comunes
    common_contingencies_company: Decimal = Decimal("23.60")  # Empresa
    common_contingencies_worker: Decimal = Decimal("4.70")    # Treballador
    
    # Desocupació
    unemployment_company: Decimal = Decimal("5.50")           # Empresa (contracte indefinit)
    unemployment_worker: Decimal = Decimal("1.55")            # Treballador
    
    # Formació professional
    professional_training_company: Decimal = Decimal("0.60")  # Empresa
    professional_training_worker: Decimal = Decimal("0.10")   # Treballador
    
    # FOGASA (Fons de Garantia Salarial)
    fogasa_company: Decimal = Decimal("0.20")                 # Només empresa
    
    @property
    def total_company_percentage(self) -> Decimal:
        """Percentatge total a càrrec de l'empresa."""
        return (
            self.common_contingencies_company +
            self.unemployment_company +
            self.professional_training_company +
            self.fogasa_company
        )
    
    @property
    def total_worker_percentage(self) -> Decimal:
        """Percentatge total a càrrec del treballador."""
        return (
            self.common_contingencies_worker +
            self.unemployment_worker +
            self.professional_training_worker
        )


class SocialSecurityCalculator:
    """
    Calculadora de cotitzacions a la Seguretat Social.
    Taules oficials 2024 per a règim general.
    """
    
    # Definició dels 11 grups de cotització (2024)
    # Fonts: Ministerio de Inclusión, Seguridad Social y Migraciones
    GROUPS = {
        1: SocialSecurityGroup(
            group_number=1,
            name="Enginyers i llicenciats. Personal d'alta direcció",
            min_base=Decimal("1629.00"),
            max_base=Decimal("4495.50")
        ),
        2: SocialSecurityGroup(
            group_number=2,
            name="Enginyers tècnics, perits i ajudants titulats",
            min_base=Decimal("1351.20"),
            max_base=Decimal("4495.50")
        ),
        3: SocialSecurityGroup(
            group_number=3,
            name="Caps administratius i de taller",
            min_base=Decimal("1174.20"),
            max_base=Decimal("4495.50")
        ),
        4: SocialSecurityGroup(
            group_number=4,
            name="Ajudants no titulats",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
        5: SocialSecurityGroup(
            group_number=5,
            name="Oficials administratius",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
        6: SocialSecurityGroup(
            group_number=6,
            name="Subalterns",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
        7: SocialSecurityGroup(
            group_number=7,
            name="Auxiliars administratius",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
        8: SocialSecurityGroup(
            group_number=8,
            name="Oficials de primera i segona",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
        9: SocialSecurityGroup(
            group_number=9,
            name="Oficials de tercera i especialistes",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
        10: SocialSecurityGroup(
            group_number=10,
            name="Peons",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
        11: SocialSecurityGroup(
            group_number=11,
            name="Treballadors menors de 18 anys",
            min_base=Decimal("1110.00"),
            max_base=Decimal("4495.50")
        ),
    }
    
    @staticmethod
    def get_group(group_number: int) -> SocialSecurityGroup:
        """Obté el grup de cotització per número."""
        if group_number not in SocialSecurityCalculator.GROUPS:
            raise ValueError(f"Grup de cotització {group_number} no vàlid. Ha de ser entre 1 i 11.")
        return SocialSecurityCalculator.GROUPS[group_number]
    
    @staticmethod
    def calculate_contribution_base(
        gross_salary: Decimal,
        group_number: int
    ) -> Decimal:
        """
        Calcula la base de cotització aplicant límits mínim i màxim.
        
        Args:
            gross_salary: Salari brut mensual
            group_number: Grup de cotització (1-11)
        
        Returns:
            Base de cotització ajustada
        """
        group = SocialSecurityCalculator.get_group(group_number)
        
        # Aplicar límits
        if gross_salary < group.min_base:
            return group.min_base
        elif gross_salary > group.max_base:
            return group.max_base
        else:
            return gross_salary
    
    @staticmethod
    def calculate_company_contribution(
        gross_salary: Decimal,
        group_number: int
    ) -> Tuple[Decimal, Dict[str, Decimal]]:
        """
        Calcula la cotització a càrrec de l'empresa.
        
        Returns:
            Tuple amb (total, desglossament per conceptes)
        """
        group = SocialSecurityCalculator.get_group(group_number)
        base = SocialSecurityCalculator.calculate_contribution_base(gross_salary, group_number)
        
        breakdown = {
            "base_cotitzacio": base,
            "contingencies_comunes": (base * group.common_contingencies_company / 100).quantize(Decimal("0.01")),
            "desocupacio": (base * group.unemployment_company / 100).quantize(Decimal("0.01")),
            "formacio_professional": (base * group.professional_training_company / 100).quantize(Decimal("0.01")),
            "fogasa": (base * group.fogasa_company / 100).quantize(Decimal("0.01")),
        }
        
        total = sum(v for k, v in breakdown.items() if k != "base_cotitzacio")
        
        return total, breakdown
    
    @staticmethod
    def calculate_worker_contribution(
        gross_salary: Decimal,
        group_number: int
    ) -> Tuple[Decimal, Dict[str, Decimal]]:
        """
        Calcula la cotització a càrrec del treballador.
        
        Returns:
            Tuple amb (total, desglossament per conceptes)
        """
        group = SocialSecurityCalculator.get_group(group_number)
        base = SocialSecurityCalculator.calculate_contribution_base(gross_salary, group_number)
        
        breakdown = {
            "base_cotitzacio": base,
            "contingencies_comunes": (base * group.common_contingencies_worker / 100).quantize(Decimal("0.01")),
            "desocupacio": (base * group.unemployment_worker / 100).quantize(Decimal("0.01")),
            "formacio_professional": (base * group.professional_training_worker / 100).quantize(Decimal("0.01")),
        }
        
        total = sum(v for k, v in breakdown.items() if k != "base_cotitzacio")
        
        return total, breakdown
    
    @staticmethod
    def calculate_total_contributions(
        gross_salary: Decimal,
        group_number: int
    ) -> Dict[str, any]:
        """
        Calcula totes les cotitzacions (empresa + treballador).
        
        Returns:
            Diccionari amb tots els càlculs
        """
        company_total, company_breakdown = SocialSecurityCalculator.calculate_company_contribution(
            gross_salary, group_number
        )
        worker_total, worker_breakdown = SocialSecurityCalculator.calculate_worker_contribution(
            gross_salary, group_number
        )
        
        return {
            "base_cotitzacio": company_breakdown["base_cotitzacio"],
            "empresa": {
                "total": company_total,
                "desglossament": company_breakdown
            },
            "treballador": {
                "total": worker_total,
                "desglossament": worker_breakdown
            },
            "total_general": company_total + worker_total
        }
    
    @staticmethod
    def get_group_info(group_number: int) -> Dict[str, any]:
        """Obté informació completa d'un grup de cotització."""
        group = SocialSecurityCalculator.get_group(group_number)
        return {
            "numero": group.group_number,
            "nom": group.name,
            "base_minima": float(group.min_base),
            "base_maxima": float(group.max_base),
            "percentatge_empresa": float(group.total_company_percentage),
            "percentatge_treballador": float(group.total_worker_percentage),
            "percentatge_total": float(group.total_company_percentage + group.total_worker_percentage)
        }
