package cat.contacat.erp.core.journal.application;

import java.math.BigDecimal;

public record JournalLineCommand(
    String accountCode,
    BigDecimal debit,
    BigDecimal credit,
    String description
) {
}
