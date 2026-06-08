package cat.contacat.erp.core.product;

public class ProductNotFoundException extends RuntimeException {

    public ProductNotFoundException(String companyId, String productId) {
        super("No s'ha trobat el producte " + productId + " per a l'empresa " + companyId);
    }
}
