package cat.contacat.erp.core.company;

public class CompanyNotFoundException extends RuntimeException {

    public CompanyNotFoundException(String id) {
        super("Company " + id + " was not found");
    }
}
