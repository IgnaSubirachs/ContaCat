package cat.contacat.erp.core.partner;

public class PartnerNotFoundException extends RuntimeException {

    public PartnerNotFoundException(String companyId, String partnerId) {
        super("No s'ha trobat el partner " + partnerId + " per a l'empresa " + companyId);
    }
}
