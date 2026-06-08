package cat.contacat.erp.core.account;

public class AccountAlreadyExistsException extends RuntimeException {

    public AccountAlreadyExistsException(String companyId, String code) {
        super("Ja existeix un compte amb codi '" + code + "' per a l'empresa " + companyId);
    }
}
