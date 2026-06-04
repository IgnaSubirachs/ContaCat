package cat.contacat.erp.core.sequence;

public class DocumentSequenceNotFoundException extends RuntimeException {

    public DocumentSequenceNotFoundException(String companyId, String documentType, String series, int fiscalYear) {
        super("No active sequence found for company=%s documentType=%s series=%s fiscalYear=%d"
            .formatted(companyId, documentType, series, fiscalYear));
    }
}
