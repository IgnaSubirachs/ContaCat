package cat.contacat.erp.core.partner;

public class PartnerAlreadyExistsException extends RuntimeException {

    public PartnerAlreadyExistsException(String companyId, String taxId) {
        super("Ja existeix un partner amb NIF/CIF '" + taxId + "' per a l'empresa " + companyId);
    }
}
