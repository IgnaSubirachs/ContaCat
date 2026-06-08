package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;
import java.util.List;

public record BalanceSheetGroup(
    String name,
    BigDecimal total,
    List<BalanceSheetAccountLine> accounts
) {
}
