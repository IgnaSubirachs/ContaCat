package cat.contacat.erp.core.account;

public enum AccountType {
    ASSET,
    LIABILITY,
    EQUITY,
    INCOME,
    EXPENSE;

    public boolean isDebitNature() {
        return this == ASSET || this == EXPENSE;
    }
}
