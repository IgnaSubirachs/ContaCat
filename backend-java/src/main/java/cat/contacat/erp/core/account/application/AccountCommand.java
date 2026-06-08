package cat.contacat.erp.core.account.application;

import cat.contacat.erp.core.account.AccountType;

public record AccountCommand(
    String code,
    String name,
    AccountType accountType,
    int group,
    String parentAccountId,
    Boolean active
) {
}
