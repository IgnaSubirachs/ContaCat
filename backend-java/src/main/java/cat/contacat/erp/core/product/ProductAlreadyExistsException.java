package cat.contacat.erp.core.product;

public class ProductAlreadyExistsException extends RuntimeException {

    public ProductAlreadyExistsException(String companyId, String sku) {
        super("Ja existeix un producte amb SKU '" + sku + "' per a l'empresa " + companyId);
    }
}
