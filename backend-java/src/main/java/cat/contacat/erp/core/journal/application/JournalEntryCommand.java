package cat.contacat.erp.core.journal.application;

import java.time.LocalDate;
import java.util.List;

public record JournalEntryCommand(
    LocalDate entryDate,
    String description,
    String attachmentPath,
    List<JournalLineCommand> lines
) {
}
