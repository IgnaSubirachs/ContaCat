package cat.contacat.erp.core.licensing;

import java.util.Arrays;
import java.util.Locale;

public enum ErpModule {
    PARTNERS("partners", "Clients i proveidors", "Vendes i relacions", true),
    QUOTES("quotes", "Pressupostos comercials", "Vendes i relacions", true),
    SALES_ORDERS("sales_orders", "Comandes de venda", "Vendes i relacions", true),
    SALES_INVOICES("sales_invoices", "Factures de venda", "Vendes i relacions", true),
    PURCHASES("purchases", "Compres", "Compres", true),
    ACCOUNTING("accounting", "Comptabilitat", "Finances i comptabilitat", true),
    ACCOUNTS("accounts", "Pla comptable", "Finances i comptabilitat", true),
    TREASURY("treasury", "Tresoreria", "Finances i comptabilitat", true),
    BANKING("banking", "Conciliacio bancaria", "Finances i comptabilitat", true),
    FISCAL("fiscal", "Fiscalitat", "Finances i comptabilitat", true),
    BUDGETS("budgets", "Pressupostos", "Finances i comptabilitat", true),
    ASSETS("assets", "Actius fixos", "Finances i comptabilitat", true),
    INVENTORY("inventory", "Inventari", "Operacions", true),
    ANALYTICS("analytics", "Analitica", "Operacions", true),
    EMPLOYEES("employees", "Empleats", "Recursos humans", true),
    PAYROLLS("payrolls", "Nomines", "Recursos humans", true),
    USERS("users", "Usuaris i seguretat", "Administracio", true),
    SETTINGS("settings", "Configuracio", "Administracio", true),
    AI("ai", "Assistent IA", "Administracio", true);

    private final String key;
    private final String displayName;
    private final String category;
    private final boolean defaultEnabled;

    ErpModule(String key, String displayName, String category, boolean defaultEnabled) {
        this.key = key;
        this.displayName = displayName;
        this.category = category;
        this.defaultEnabled = defaultEnabled;
    }

    public String getKey() {
        return key;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getCategory() {
        return category;
    }

    public boolean isDefaultEnabled() {
        return defaultEnabled;
    }

    public static ErpModule fromKey(String key) {
        String normalizedKey = key == null ? "" : key.trim().toLowerCase(Locale.ROOT);
        return Arrays.stream(values())
            .filter(module -> module.key.equals(normalizedKey))
            .findFirst()
            .orElseThrow(() -> new ModuleLicenseValidationException("El modul '" + key + "' no existeix al cataleg."));
    }
}
