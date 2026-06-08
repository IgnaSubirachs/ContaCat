package cat.contacat.erp.core.warehouse.application;

public record WarehouseCommand(
    String code,
    String name,
    Boolean active
) {
}
