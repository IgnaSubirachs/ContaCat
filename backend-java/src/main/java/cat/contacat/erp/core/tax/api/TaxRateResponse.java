package cat.contacat.erp.core.tax.api;

import cat.contacat.erp.core.tax.TaxRate;
import java.math.BigDecimal;

public record TaxRateResponse(
    String id,
    String companyId,
    String code,
    String name,
    BigDecimal rate,
    String taxType,
    String inputAccountCode,
    String outputAccountCode,
    boolean active
) {

    public static TaxRateResponse from(TaxRate taxRate) {
        return new TaxRateResponse(
            taxRate.getId(),
            taxRate.getCompany().getId(),
            taxRate.getCode(),
            taxRate.getName(),
            taxRate.getRate(),
            taxRate.getTaxType(),
            taxRate.getInputAccountCode(),
            taxRate.getOutputAccountCode(),
            taxRate.isActive()
        );
    }
}
