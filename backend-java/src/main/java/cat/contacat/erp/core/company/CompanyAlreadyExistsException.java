package cat.contacat.erp.core.company;

public class CompanyAlreadyExistsException extends RuntimeException {

    public CompanyAlreadyExistsException(String taxId) {
        super("Company with tax id " + taxId + " already exists");
    }
}
