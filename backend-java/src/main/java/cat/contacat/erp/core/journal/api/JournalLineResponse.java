package cat.contacat.erp.core.journal.api;

import cat.contacat.erp.core.journal.JournalLine;
import java.math.BigDecimal;

public record JournalLineResponse(
    String id,
    String accountId,
    String accountCode,
    String accountName,
    int lineOrder,
    BigDecimal debit,
    BigDecimal credit,
    String description
) {

    public static JournalLineResponse from(JournalLine line) {
        return new JournalLineResponse(
            line.getId(),
            line.getAccount().getId(),
            line.getAccount().getCode(),
            line.getAccount().getName(),
            line.getLineOrder(),
            line.getDebit(),
            line.getCredit(),
            line.getDescription()
        );
    }
}
