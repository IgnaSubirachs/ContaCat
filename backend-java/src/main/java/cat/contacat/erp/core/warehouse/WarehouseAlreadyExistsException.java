package cat.contacat.erp.core.warehouse;

public class WarehouseAlreadyExistsException extends RuntimeException {

    public WarehouseAlreadyExistsException(String companyId, String code) {
        super("Ja existeix un magatzem amb codi '" + code + "' per a l'empresa " + companyId);
    }
}
