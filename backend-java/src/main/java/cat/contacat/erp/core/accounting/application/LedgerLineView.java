package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;
import java.time.LocalDate;

public record LedgerLineView(
    String journalEntryId,
    int entryNumber,
    String formattedNumber,
    LocalDate entryDate,
    String entryDescription,
    String lineDescription,
    BigDecimal debit,
    BigDecimal credit,
    BigDecimal runningBalance
) {
}
