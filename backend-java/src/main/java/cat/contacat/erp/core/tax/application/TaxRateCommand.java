package cat.contacat.erp.core.tax.application;

import java.math.BigDecimal;

public record TaxRateCommand(
    String code,
    String name,
    BigDecimal rate,
    String taxType,
    String inputAccountCode,
    String outputAccountCode,
    Boolean active
) {
}
