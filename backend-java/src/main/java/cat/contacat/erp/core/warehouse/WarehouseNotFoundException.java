package cat.contacat.erp.core.warehouse;

public class WarehouseNotFoundException extends RuntimeException {

    public WarehouseNotFoundException(String companyId, String warehouseId) {
        super("No s'ha trobat el magatzem " + warehouseId + " per a l'empresa " + companyId);
    }
}
