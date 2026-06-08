package cat.contacat.erp.core.accounting.application;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public record ProfitLossReport(
    LocalDate startDate,
    LocalDate endDate,
    List<ProfitLossGroup> groups,
    BigDecimal operatingResult,
    BigDecimal financialResult,
    BigDecimal resultBeforeTax,
    BigDecimal resultForYear
) {
}
