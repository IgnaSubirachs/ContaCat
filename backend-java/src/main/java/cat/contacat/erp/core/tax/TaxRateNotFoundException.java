package cat.contacat.erp.core.tax;

public class TaxRateNotFoundException extends RuntimeException {

    public TaxRateNotFoundException(String companyId, String taxRateId) {
        super("No s'ha trobat l'impost " + taxRateId + " per a l'empresa " + companyId);
    }
}
