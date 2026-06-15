package cat.contacat.erp.core.journal.importer;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDate;
import org.junit.jupiter.api.Test;

class InvoiceTextInterpreterTest {

    private final InvoiceTextInterpreter interpreter = new InvoiceTextInterpreter();

    @Test
    void interpretsCommonSupplierInvoiceAmounts() {
        InvoiceDocumentData result = interpreter.interpret("""
            FACTURA FV-2026/44
            EMPRESA PROVEIDORA SL - CIF B12345678
            Data: 15/06/2026
            Base imposable: 100,00 EUR
            Quota IVA: 21,00 EUR
            Total factura: 121,00 EUR
            """);

        assertThat(result.invoiceNumber()).isEqualTo("FV-2026/44");
        assertThat(result.supplierName()).isEqualTo("EMPRESA PROVEIDORA SL");
        assertThat(result.supplierTaxId()).isEqualTo("B12345678");
        assertThat(result.invoiceDate()).isEqualTo(LocalDate.of(2026, 6, 15));
        assertThat(result.taxableBase()).isEqualByComparingTo("100.00");
        assertThat(result.taxAmount()).isEqualByComparingTo("21.00");
        assertThat(result.total()).isEqualByComparingTo("121.00");
        assertThat(result.warnings()).isEmpty();
    }

    @Test
    void calculatesMissingBaseAndReturnsReviewWarning() {
        InvoiceDocumentData result = interpreter.interpret("""
            Factura A-19
            PROVEIDOR EXEMPLE SL - CIF B12345678
            IVA: 10,50
            Total: 60,50
            """);

        assertThat(result.taxableBase()).isEqualByComparingTo("50.00");
        assertThat(result.warnings()).contains("Base imposable calculada a partir del total i l'IVA");
    }

    @Test
    void interpretsMirayImporterMobileInvoiceFormat() {
        InvoiceDocumentData result = interpreter.interpret("""
            MIRAY OPERADOR
            MIRAY CONSULTING SL - CIF B64242613
            Factura 202624
            Emision: 02/04/2026
            Base imponible 60.00 EUR
            IVA (21%) 12.60 EUR
            Total Factura 72.60 EUR
            """);

        assertThat(result.invoiceNumber()).isEqualTo("202624");
        assertThat(result.invoiceDate()).isEqualTo(LocalDate.of(2026, 4, 2));
        assertThat(result.supplierName()).isEqualTo("MIRAY CONSULTING SL");
        assertThat(result.supplierTaxId()).isEqualTo("B64242613");
        assertThat(result.taxableBase()).isEqualByComparingTo("60.00");
        assertThat(result.taxAmount()).isEqualByComparingTo("12.60");
        assertThat(result.total()).isEqualByComparingTo("72.60");
        assertThat(result.warnings()).isEmpty();
    }
}
