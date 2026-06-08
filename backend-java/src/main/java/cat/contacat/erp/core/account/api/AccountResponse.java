package cat.contacat.erp.core.account.api;

import cat.contacat.erp.core.account.Account;
import cat.contacat.erp.core.account.AccountType;
import java.time.OffsetDateTime;

public record AccountResponse(
    String id,
    String companyId,
    String code,
    String name,
    AccountType accountType,
    int group,
    String parentAccountId,
    boolean active,
    OffsetDateTime createdAt,
    OffsetDateTime updatedAt
) {

    public static AccountResponse from(Account account) {
        return new AccountResponse(
            account.getId(),
            account.getCompany().getId(),
            account.getCode(),
            account.getName(),
            account.getAccountType(),
            account.getGroup(),
            account.getParentAccount() == null ? null : account.getParentAccount().getId(),
            account.isActive(),
            account.getCreatedAt(),
            account.getUpdatedAt()
        );
    }
}
