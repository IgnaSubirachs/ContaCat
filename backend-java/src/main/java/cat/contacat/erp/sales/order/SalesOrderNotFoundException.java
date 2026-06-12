package cat.contacat.erp.sales.order;

public class SalesOrderNotFoundException extends RuntimeException {
    public SalesOrderNotFoundException(String companyId, String orderId) {
        super("No s'ha trobat la comanda " + orderId + " per a l'empresa " + companyId);
    }
}
