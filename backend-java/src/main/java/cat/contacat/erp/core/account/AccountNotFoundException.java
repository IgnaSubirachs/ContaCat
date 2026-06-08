package cat.contacat.erp.core.account;

public class AccountNotFoundException extends RuntimeException {

    public AccountNotFoundException(String companyId, String accountIdOrCode) {
        super("No s'ha trobat el compte " + accountIdOrCode + " per a l'empresa " + companyId);
    }
}
