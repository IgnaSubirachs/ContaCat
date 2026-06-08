package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;
import java.util.List;

public record ProfitLossGroup(
    String name,
    BigDecimal total,
    List<ProfitLossAccountLine> lines
) {
}
