package cat.contacat.erp.core.journal.api;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;
import java.util.List;

public record JournalEntryRequest(
    @NotNull LocalDate entryDate,
    @NotBlank @Size(max = 500) String description,
    @Size(max = 255) String attachmentPath,
    @NotEmpty List<@Valid JournalLineRequest> lines
) {
}
