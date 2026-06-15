package cat.contacat.erp.core.journal.api;

import static org.assertj.core.api.Assertions.assertThat;

import cat.contacat.erp.core.journal.importer.InvoiceImportResult;
import cat.contacat.erp.core.journal.importer.SupplierResolutionStatus;
import java.util.List;
import org.junit.jupiter.api.Test;

class InvoiceImportResponseTest {

    @Test
    void requestsSupplierCreationOnlyWhenSupplierWasNotFound() {
        InvoiceImportResponse notFound = InvoiceImportResponse.from(result(SupplierResolutionStatus.NOT_FOUND));
        InvoiceImportResponse notUsable = InvoiceImportResponse.from(result(SupplierResolutionStatus.NOT_USABLE));

        assertThat(notFound.draftEntry()).isNull();
        assertThat(notFound.supplierCreationRequired()).isTrue();
        assertThat(notUsable.supplierCreationRequired()).isFalse();
    }

    private InvoiceImportResult result(SupplierResolutionStatus status) {
        return new InvoiceImportResult(null, "Proveidor", "B12345678", null, status, 80, List.of());
    }
}
