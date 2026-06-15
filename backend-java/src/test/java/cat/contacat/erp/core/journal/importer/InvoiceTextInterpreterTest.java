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
            Data: 15/06/2026
            Base imposable: 100,00 EUR
            Quota IVA: 21,00 EUR
            Total factura: 121,00 EUR
            """);

        assertThat(result.invoiceNumber()).isEqualTo("FV-2026/44");
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
            IVA: 10,50
            Total: 60,50
            """);

        assertThat(result.taxableBase()).isEqualByComparingTo("50.00");
        assertThat(result.warnings()).contains("Base imposable calculada a partir del total i l'IVA");
    }
}
