package cat.contacat.erp.sales.invoice;

public class SalesInvoiceNotFoundException extends RuntimeException {
    public SalesInvoiceNotFoundException(String companyId, String invoiceId) {
        super("No s'ha trobat la factura " + invoiceId + " per a l'empresa " + companyId);
    }
}
