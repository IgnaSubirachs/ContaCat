package cat.contacat.erp.sales.order.application;

import java.time.LocalDate;
import java.util.List;

public record SalesOrderCommand(
    String partnerId,
    String series,
    LocalDate orderDate,
    LocalDate deliveryDate,
    String deliveryAddress,
    String notes,
    List<SalesOrderLineCommand> lines
) {
}
