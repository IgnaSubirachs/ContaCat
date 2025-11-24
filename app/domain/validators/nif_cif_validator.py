"""
Validador oficial de NIF, CIF i NIE segons normativa espanyola.
"""
import re


class DocumentValidator:
    """Validador de documents d'identificació espanyols."""
    
    # Lletres de control per NIF
    NIF_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
    
    # Lletres vàlides per CIF
    CIF_LETTERS = "JABCDEFGHI"
    
    # Tipus d'organització per CIF
    CIF_ORG_TYPES = "ABCDEFGHJNPQRSUVW"
    
    @staticmethod
    def validate_nif(nif: str) -> bool:
        """
        Valida un NIF (DNI) espanyol.
        Format: 8 dígits + 1 lletra de control
        """
        if not nif:
            return False
        
        nif = nif.upper().strip().replace("-", "").replace(" ", "")
        
        # Comprovar format: 8 dígits + 1 lletra
        if not re.match(r'^\d{8}[A-Z]$', nif):
            return False
        
        # Extreure número i lletra
        number = int(nif[:-1])
        letter = nif[-1]
        
        # Calcular lletra de control
        expected_letter = DocumentValidator.NIF_LETTERS[number % 23]
        
        return letter == expected_letter
    
    @staticmethod
    def validate_nie(nie: str) -> bool:
        """
        Valida un NIE (Número d'Identificació d'Estranger).
        Format: X/Y/Z + 7 dígits + 1 lletra de control
        """
        if not nie:
            return False
        
        nie = nie.upper().strip().replace("-", "").replace(" ", "")
        
        # Comprovar format: X/Y/Z + 7 dígits + lletra
        if not re.match(r'^[XYZ]\d{7}[A-Z]$', nie):
            return False
        
        # Convertir primera lletra a número (X=0, Y=1, Z=2)
        replacements = {'X': '0', 'Y': '1', 'Z': '2'}
        nie_number = replacements[nie[0]] + nie[1:-1]
        
        # Calcular lletra de control
        number = int(nie_number)
        letter = nie[-1]
        expected_letter = DocumentValidator.NIF_LETTERS[number % 23]
        
        return letter == expected_letter
    
    @staticmethod
    def validate_cif(cif: str) -> bool:
        """
        Valida un CIF (Codi d'Identificació Fiscal) espanyol.
        Format: 1 lletra + 7 dígits + 1 dígit/lletra de control
        """
        if not cif:
            return False
        
        cif = cif.upper().strip().replace("-", "").replace(" ", "")
        
        # Comprovar format: lletra + 7 dígits + dígit/lletra
        if not re.match(r'^[A-Z]\d{7}[A-Z0-9]$', cif):
            return False
        
        # Comprovar que la primera lletra sigui vàlida
        if cif[0] not in DocumentValidator.CIF_ORG_TYPES:
            return False
        
        # Calcular dígit de control
        org_type = cif[0]
        digits = cif[1:8]
        control = cif[8]
        
        # Suma parells i senars
        sum_a = sum(int(digits[i]) for i in range(1, 7, 2))
        sum_b = 0
        for i in range(0, 7, 2):
            doubled = int(digits[i]) * 2
            sum_b += doubled // 10 + doubled % 10
        
        total = sum_a + sum_b
        unit_digit = total % 10
        control_digit = (10 - unit_digit) % 10
        
        # Segons el tipus d'organització, el control és dígit o lletra
        if org_type in "NPQRSW":
            # Control és una lletra
            expected_control = DocumentValidator.CIF_LETTERS[control_digit]
            return control == expected_control
        else:
            # Control pot ser dígit o lletra
            expected_digit = str(control_digit)
            expected_letter = DocumentValidator.CIF_LETTERS[control_digit]
            return control == expected_digit or control == expected_letter
    
    @staticmethod
    def validate_document(document: str) -> tuple[bool, str]:
        """
        Valida qualsevol tipus de document espanyol (NIF, NIE, CIF).
        Retorna (és_vàlid, tipus_document)
        """
        if not document:
            return False, "INVALID"
        
        document = document.upper().strip().replace("-", "").replace(" ", "")
        
        # Intentar validar com a NIE (comença amb X, Y, Z)
        if document and document[0] in "XYZ":
            if DocumentValidator.validate_nie(document):
                return True, "NIE"
            return False, "INVALID"
        
        # Intentar validar com a CIF (comença amb lletra)
        if document and document[0].isalpha():
            if DocumentValidator.validate_cif(document):
                return True, "CIF"
            return False, "INVALID"
        
        # Intentar validar com a NIF (comença amb dígit)
        if document and document[0].isdigit():
            if DocumentValidator.validate_nif(document):
                return True, "NIF"
            return False, "INVALID"
        
        return False, "INVALID"
    
    @staticmethod
    def format_document(document: str) -> str:
        """
        Formata un document eliminant espais i guions.
        """
        if not document:
            return ""
        return document.upper().strip().replace("-", "").replace(" ", "")
