package cat.contacat.erp.core.tax;

public class TaxRateAlreadyExistsException extends RuntimeException {

    public TaxRateAlreadyExistsException(String companyId, String code) {
        super("Ja existeix un impost amb codi '" + code + "' per a l'empresa " + companyId);
    }
}
