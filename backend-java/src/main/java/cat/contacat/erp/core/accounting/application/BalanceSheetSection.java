package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;
import java.util.List;

public record BalanceSheetSection(
    BigDecimal total,
    List<BalanceSheetGroup> groups
) {
}
