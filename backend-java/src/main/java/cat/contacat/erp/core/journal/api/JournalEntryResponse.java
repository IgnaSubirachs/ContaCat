package cat.contacat.erp.core.journal.api;

import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.JournalEntryStatus;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

public record JournalEntryResponse(
    String id,
    String companyId,
    int entryNumber,
    String formattedNumber,
    LocalDate entryDate,
    String description,
    JournalEntryStatus status,
    String attachmentPath,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt,
    OffsetDateTime postedAt,
    List<JournalLineResponse> lines
) {

    public static JournalEntryResponse from(JournalEntry entry) {
        return new JournalEntryResponse(
            entry.getId(),
            entry.getCompany().getId(),
            entry.getEntryNumber(),
            entry.getFormattedNumber(),
            entry.getEntryDate(),
            entry.getDescription(),
            entry.getStatus(),
            entry.getAttachmentPath(),
            entry.getCreatedAt(),
            entry.getUpdatedAt(),
            entry.getPostedAt(),
            entry.getLines().stream().map(JournalLineResponse::from).toList()
        );
    }
}
