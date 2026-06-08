package cat.contacat.erp.core.accounting.application;

import cat.contacat.erp.core.account.AccountType;
import java.math.BigDecimal;

public record TrialBalanceLine(
    String accountId,
    String accountCode,
    String accountName,
    AccountType accountType,
    BigDecimal balance
) {
}
