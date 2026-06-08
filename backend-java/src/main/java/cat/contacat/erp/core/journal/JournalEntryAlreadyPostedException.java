package cat.contacat.erp.core.journal;

public class JournalEntryAlreadyPostedException extends RuntimeException {

    public JournalEntryAlreadyPostedException(String entryId) {
        super("L'assentament " + entryId + " ja esta comptabilitzat");
    }
}
