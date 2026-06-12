package cat.contacat.erp.sales.quote;

public class QuoteNotFoundException extends RuntimeException {

    public QuoteNotFoundException(String companyId, String quoteId) {
        super("No s'ha trobat el pressupost " + quoteId + " per a l'empresa " + companyId);
    }
}
