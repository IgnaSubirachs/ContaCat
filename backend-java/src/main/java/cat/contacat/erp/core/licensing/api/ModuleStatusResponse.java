package cat.contacat.erp.core.licensing.api;

public record ModuleStatusResponse(
    String companyId,
    String moduleKey,
    boolean enabled
) {
}
