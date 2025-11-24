"""
Calculadora de retenció d'IRPF segons taules oficials 2024.
Simplificació per a càlcul bàsic.
"""
from decimal import Decimal
from typing import Optional


class IRPFCalculator:
    """
    Calculadora de retenció d'IRPF.
    Nota: Aquesta és una versió simplificada. Per a càlculs oficials,
    consultar les taules de l'Agència Tributària.
    """
    
    # Taules simplificades de retenció IRPF 2024 (%)
    # Basat en salari brut anual
    RETENTION_TABLE = [
        (12450, 0),      # Fins a 12.450€ -> 0% (mínim exempt)
        (20200, 19),     # De 12.450€ a 20.200€ -> 19%
        (35200, 24),     # De 20.200€ a 35.200€ -> 24%
        (60000, 30),     # De 35.200€ a 60.000€ -> 30%
        (300000, 37),    # De 60.000€ a 300.000€ -> 37%
        (float('inf'), 45)  # Més de 300.000€ -> 45%
    ]
    
    # Reducció per fills a càrrec (punts percentuals)
    CHILDREN_REDUCTION = {
        0: 0,
        1: 2,
        2: 3.5,
        3: 5,
        4: 6,
    }
    
    # Reducció per discapacitat (punts percentuals)
    DISABILITY_REDUCTION = {
        0: 0,      # Sense discapacitat
        33: 2,     # 33-64% discapacitat
        65: 4,     # 65% o més discapacitat
    }
    
    @staticmethod
    def calculate_retention(
        annual_salary: Decimal,
        children_count: int = 0,
        disability_degree: int = 0,
        marital_status: str = "SINGLE"
    ) -> Decimal:
        """
        Calcula el percentatge de retenció d'IRPF.
        
        Args:
            annual_salary: Salari brut anual
            children_count: Nombre de fills a càrrec
            disability_degree: Grau de discapacitat (0, 33, 65)
            marital_status: Estat civil (SINGLE, MARRIED, etc.)
        
        Returns:
            Percentatge de retenció (0-100)
        """
        if annual_salary <= 0:
            return Decimal("0")
        
        # Determinar tram de retenció base
        base_retention = Decimal("0")
        for limit, retention in IRPFCalculator.RETENTION_TABLE:
            if annual_salary <= limit:
                base_retention = Decimal(str(retention))
                break
        
        # Aplicar reduccions per fills
        children_reduction = Decimal("0")
        if children_count > 0:
            if children_count >= 4:
                children_reduction = Decimal(str(IRPFCalculator.CHILDREN_REDUCTION[4]))
            else:
                children_reduction = Decimal(str(IRPFCalculator.CHILDREN_REDUCTION[children_count]))
        
        # Aplicar reducció per discapacitat
        disability_reduction = Decimal("0")
        if disability_degree >= 65:
            disability_reduction = Decimal(str(IRPFCalculator.DISABILITY_REDUCTION[65]))
        elif disability_degree >= 33:
            disability_reduction = Decimal(str(IRPFCalculator.DISABILITY_REDUCTION[33]))
        
        # Càlcul final
        final_retention = base_retention - children_reduction - disability_reduction
        
        # Mínim 0%, màxim 45%
        if final_retention < 0:
            final_retention = Decimal("0")
        if final_retention > 45:
            final_retention = Decimal("45")
        
        return final_retention
    
    @staticmethod
    def calculate_monthly_retention_amount(
        monthly_salary: Decimal,
        retention_percentage: Decimal
    ) -> Decimal:
        """
        Calcula l'import mensual retingut d'IRPF.
        """
        return (monthly_salary * retention_percentage / 100).quantize(Decimal("0.01"))
    
    @staticmethod
    def get_net_salary(
        gross_salary: Decimal,
        retention_percentage: Decimal
    ) -> Decimal:
        """
        Calcula el salari net després de retenció d'IRPF.
        """
        retention_amount = IRPFCalculator.calculate_monthly_retention_amount(
            gross_salary, retention_percentage
        )
        return gross_salary - retention_amount
