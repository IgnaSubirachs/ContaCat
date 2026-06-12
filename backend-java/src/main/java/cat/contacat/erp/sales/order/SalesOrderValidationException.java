package cat.contacat.erp.sales.order;

public class SalesOrderValidationException extends RuntimeException {
    public SalesOrderValidationException(String message) {
        super(message);
    }
}
