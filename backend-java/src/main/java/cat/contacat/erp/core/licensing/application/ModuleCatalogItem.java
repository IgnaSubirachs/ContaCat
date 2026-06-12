package cat.contacat.erp.core.licensing.application;

public record ModuleCatalogItem(
    String key,
    String displayName,
    String category,
    boolean defaultEnabled
) {
}
