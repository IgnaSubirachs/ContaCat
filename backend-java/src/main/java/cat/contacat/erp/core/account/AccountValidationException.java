package cat.contacat.erp.core.account;

public class AccountValidationException extends RuntimeException {

    public AccountValidationException(String message) {
        super(message);
    }
}
