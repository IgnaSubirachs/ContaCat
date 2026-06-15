package cat.contacat.erp.core.journal.importer;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.JournalEntryStatus;
import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class InvoiceImportApplicationServiceTest {

    @Mock private InvoiceDocumentReader reader;
    @Mock private JournalEntryApplicationService journalEntryService;

    @Test
    void importCreatesEditableDraftAndNeverPostsIt() {
        byte[] document = new byte[] {1, 2, 3};
        when(reader.read(document)).thenReturn(new InvoiceDocumentData(
            LocalDate.of(2026, 6, 15),
            "Proveidor",
            "F-19",
            new BigDecimal("100.00"),
            new BigDecimal("21.00"),
            new BigDecimal("121.00"),
            100,
            List.of()
        ));
        JournalEntry draft = new JournalEntry();
        draft.setStatus(JournalEntryStatus.DRAFT);
        when(journalEntryService.create(eq("company-1"), org.mockito.ArgumentMatchers.any())).thenReturn(draft);

        InvoiceImportResult result = new InvoiceImportApplicationService(reader, journalEntryService)
            .importSupplierInvoice("company-1", "factura.pdf", document);

        ArgumentCaptor<JournalEntryCommand> command = ArgumentCaptor.forClass(JournalEntryCommand.class);
        verify(journalEntryService).create(eq("company-1"), command.capture());
        assertThat(result.draftEntry().getStatus()).isEqualTo(JournalEntryStatus.DRAFT);
        assertThat(command.getValue().description()).contains("Proveidor");
        assertThat(command.getValue().lines()).extracting("accountCode").containsExactly("600000", "472000", "400000");
    }
}
