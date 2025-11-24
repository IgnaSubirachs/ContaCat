"""
Validador de Número de Seguretat Social (NSS) espanyol.
"""
import re


class NSSValidator:
    """Validador de NSS segons normativa de la Seguretat Social espanyola."""
    
    @staticmethod
    def validate_nss(nss: str) -> bool:
        """
        Valida un Número de Seguretat Social espanyol.
        Format: 12 dígits (2 província + 8 número + 2 control)
        """
        if not nss:
            return False
        
        # Netejar NSS (eliminar espais, guions, barres)
        nss = nss.strip().replace(" ", "").replace("-", "").replace("/", "")
        
        # Comprovar que siguin exactament 12 dígits
        if not re.match(r'^\d{12}$', nss):
            return False
        
        # Extreure parts
        province = nss[:2]
        number = nss[2:10]
        control = nss[10:12]
        
        # Validar província (01-99, excepte alguns no vàlids)
        province_num = int(province)
        if province_num == 0 or province_num > 99:
            return False
        
        # Calcular dígits de control
        base_number = int(province + number)
        calculated_control = base_number % 97
        
        return int(control) == calculated_control
    
    @staticmethod
    def format_nss(nss: str) -> str:
        """
        Formata un NSS amb barres.
        Exemple: 28/12345678/45
        """
        if not nss:
            return ""
        
        # Netejar NSS
        nss = nss.strip().replace(" ", "").replace("-", "").replace("/", "")
        
        if len(nss) != 12:
            return nss
        
        # Formatar: XX/XXXXXXXX/XX
        return f"{nss[:2]}/{nss[2:10]}/{nss[10:12]}"
    
    @staticmethod
    def get_province_code(nss: str) -> str:
        """
        Retorna el codi de província del NSS.
        """
        if not nss or len(nss) < 2:
            return ""
        
        nss = nss.strip().replace(" ", "").replace("-", "").replace("/", "")
        return nss[:2]
