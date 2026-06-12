package cat.contacat.erp.sales.order.api;

import java.time.LocalDate;

public record CreateOrderFromQuoteRequest(
    LocalDate orderDate
) {
}
