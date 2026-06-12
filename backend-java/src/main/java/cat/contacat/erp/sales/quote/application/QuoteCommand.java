package cat.contacat.erp.sales.quote.application;

import java.time.LocalDate;
import java.util.List;

public record QuoteCommand(
    String partnerId,
    String series,
    LocalDate quoteDate,
    LocalDate validUntil,
    String notes,
    List<QuoteLineCommand> lines
) {
}
