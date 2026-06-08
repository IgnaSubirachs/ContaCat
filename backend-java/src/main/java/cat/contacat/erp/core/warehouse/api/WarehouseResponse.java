package cat.contacat.erp.core.warehouse.api;

import cat.contacat.erp.core.warehouse.Warehouse;

public record WarehouseResponse(
    String id,
    String companyId,
    String code,
    String name,
    boolean active
) {

    public static WarehouseResponse from(Warehouse warehouse) {
        return new WarehouseResponse(
            warehouse.getId(),
            warehouse.getCompany().getId(),
            warehouse.getCode(),
            warehouse.getName(),
            warehouse.isActive()
        );
    }
}
