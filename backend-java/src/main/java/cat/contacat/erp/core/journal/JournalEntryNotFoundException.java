package cat.contacat.erp.core.journal;

public class JournalEntryNotFoundException extends RuntimeException {

    public JournalEntryNotFoundException(String companyId, String entryId) {
        super("No s'ha trobat l'assentament " + entryId + " per a l'empresa " + companyId);
    }
}
