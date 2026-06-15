package cat.contacat.erp.core.journal.importer;

public interface InvoiceDocumentReader {
    InvoiceDocumentData read(byte[] document);
}
