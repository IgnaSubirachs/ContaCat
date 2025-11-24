"""
Validador d'IBAN (International Bank Account Number).
"""
import re


class IBANValidator:
    """Validador d'IBAN segons norma ISO 13616."""
    
    # Longituds d'IBAN per país
    IBAN_LENGTHS = {
        'ES': 24,  # Espanya
        'FR': 27,  # França
        'DE': 22,  # Alemanya
        'IT': 27,  # Itàlia
        'PT': 25,  # Portugal
        'GB': 22,  # Regne Unit
        'NL': 18,  # Països Baixos
        'BE': 16,  # Bèlgica
        # Afegir més països si cal
    }
    
    @staticmethod
    def validate_iban(iban: str) -> bool:
        """
        Valida un IBAN utilitzant l'algoritme de mòdul 97.
        """
        if not iban:
            return False
        
        # Netejar IBAN (eliminar espais i convertir a majúscules)
        iban = iban.upper().strip().replace(" ", "").replace("-", "")
        
        # Comprovar format bàsic: 2 lletres + 2 dígits + fins a 30 caràcters alfanumèrics
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]+$', iban):
            return False
        
        # Comprovar longitud segons país
        country_code = iban[:2]
        if country_code in IBANValidator.IBAN_LENGTHS:
            expected_length = IBANValidator.IBAN_LENGTHS[country_code]
            if len(iban) != expected_length:
                return False
        else:
            # País no reconegut, però validem igualment
            if len(iban) < 15 or len(iban) > 34:
                return False
        
        # Moure els primers 4 caràcters al final
        rearranged = iban[4:] + iban[:4]
        
        # Convertir lletres a números (A=10, B=11, ..., Z=35)
        numeric_iban = ""
        for char in rearranged:
            if char.isdigit():
                numeric_iban += char
            else:
                numeric_iban += str(ord(char) - ord('A') + 10)
        
        # Calcular mòdul 97
        return int(numeric_iban) % 97 == 1
    
    @staticmethod
    def format_iban(iban: str) -> str:
        """
        Formata un IBAN amb espais cada 4 caràcters.
        Exemple: ES91 2100 0418 4502 0005 1332
        """
        if not iban:
            return ""
        
        # Netejar IBAN
        iban = iban.upper().strip().replace(" ", "").replace("-", "")
        
        # Afegir espais cada 4 caràcters
        return " ".join(iban[i:i+4] for i in range(0, len(iban), 4))
    
    @staticmethod
    def get_country_code(iban: str) -> str:
        """
        Retorna el codi de país de l'IBAN.
        """
        if not iban or len(iban) < 2:
            return ""
        
        iban = iban.upper().strip().replace(" ", "").replace("-", "")
        return iban[:2]
    
    @staticmethod
    def is_spanish_iban(iban: str) -> bool:
        """
        Comprova si l'IBAN és espanyol.
        """
        return IBANValidator.get_country_code(iban) == "ES"
