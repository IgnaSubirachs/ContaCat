package cat.contacat.erp.core.journal.importer;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.JournalEntryStatus;
import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.partner.PartnerRepository;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class InvoiceImportApplicationServiceTest {

    @Mock private InvoiceDocumentReader reader;
    @Mock private JournalEntryApplicationService journalEntryService;
    @Mock private PartnerRepository partnerRepository;

    @Test
    void importCreatesEditableDraftAndNeverPostsIt() {
        byte[] document = new byte[] {1, 2, 3};
        when(reader.read(document)).thenReturn(new InvoiceDocumentData(
            LocalDate.of(2026, 6, 15),
            "Proveidor",
            "B12345678",
            "F-19",
            new BigDecimal("100.00"),
            new BigDecimal("21.00"),
            new BigDecimal("121.00"),
            100,
            List.of()
        ));
        when(partnerRepository.findByCompanyIdAndTaxId("company-1", "B12345678"))
            .thenReturn(Optional.of(supplier("supplier-1", "400123")));
        JournalEntry draft = new JournalEntry();
        draft.setStatus(JournalEntryStatus.DRAFT);
        when(journalEntryService.create(eq("company-1"), org.mockito.ArgumentMatchers.any())).thenReturn(draft);

        InvoiceImportResult result = new InvoiceImportApplicationService(reader, journalEntryService, partnerRepository)
            .importSupplierInvoice("company-1", "factura.pdf", document);

        ArgumentCaptor<JournalEntryCommand> command = ArgumentCaptor.forClass(JournalEntryCommand.class);
        verify(journalEntryService).create(eq("company-1"), command.capture());
        assertThat(result.draftEntry().getStatus()).isEqualTo(JournalEntryStatus.DRAFT);
        assertThat(result.supplierResolution()).isEqualTo(SupplierResolutionStatus.FOUND);
        assertThat(result.supplierId()).isEqualTo("supplier-1");
        assertThat(command.getValue().description()).contains("Proveidor");
        assertThat(command.getValue().lines()).extracting("accountCode").containsExactly("600000", "472000", "400123");
    }

    @Test
    void importRequestsSupplierCreationAndDoesNotCreateDraftWhenSupplierIsUnknown() {
        byte[] document = new byte[] {1, 2, 3};
        when(reader.read(document)).thenReturn(invoiceData());
        when(partnerRepository.findByCompanyIdAndTaxId("company-1", "B12345678")).thenReturn(Optional.empty());

        InvoiceImportResult result = new InvoiceImportApplicationService(reader, journalEntryService, partnerRepository)
            .importSupplierInvoice("company-1", "factura.pdf", document);

        assertThat(result.draftEntry()).isNull();
        assertThat(result.supplierResolution()).isEqualTo(SupplierResolutionStatus.NOT_FOUND);
        assertThat(result.warnings()).contains("Proveidor no trobat; cal crear-lo abans de generar l'assentament");
        verify(journalEntryService, never()).create(eq("company-1"), org.mockito.ArgumentMatchers.any());
    }

    @Test
    void importUsesGenericAccountAndWarnsWhenKnownSupplierHasNoAccount() {
        byte[] document = new byte[] {1, 2, 3};
        when(reader.read(document)).thenReturn(invoiceData());
        when(partnerRepository.findByCompanyIdAndTaxId("company-1", "B12345678"))
            .thenReturn(Optional.of(supplier("supplier-1", "")));
        when(journalEntryService.create(eq("company-1"), org.mockito.ArgumentMatchers.any())).thenReturn(new JournalEntry());

        InvoiceImportResult result = new InvoiceImportApplicationService(reader, journalEntryService, partnerRepository)
            .importSupplierInvoice("company-1", "factura.pdf", document);

        ArgumentCaptor<JournalEntryCommand> command = ArgumentCaptor.forClass(JournalEntryCommand.class);
        verify(journalEntryService).create(eq("company-1"), command.capture());
        assertThat(command.getValue().lines()).extracting("accountCode").containsExactly("600000", "472000", "400000");
        assertThat(result.warnings()).contains("El proveidor no te compte comptable configurat; s'ha utilitzat el compte 400000");
    }

    @Test
    void importDoesNotOfferCreationWhenTaxIdWasNotDetected() {
        byte[] document = new byte[] {1, 2, 3};
        InvoiceDocumentData data = invoiceData(null);
        when(reader.read(document)).thenReturn(data);

        InvoiceImportResult result = new InvoiceImportApplicationService(reader, journalEntryService, partnerRepository)
            .importSupplierInvoice("company-1", "factura.pdf", document);

        assertThat(result.supplierResolution()).isEqualTo(SupplierResolutionStatus.TAX_ID_NOT_DETECTED);
        assertThat(result.warnings()).contains("No es pot cercar el proveidor sense NIF/CIF");
        verify(partnerRepository, never()).findByCompanyIdAndTaxId(eq("company-1"), org.mockito.ArgumentMatchers.any());
        verify(journalEntryService, never()).create(eq("company-1"), org.mockito.ArgumentMatchers.any());
    }

    @Test
    void importBlocksExistingPartnerThatIsNotAnActiveSupplier() {
        byte[] document = new byte[] {1, 2, 3};
        Partner customer = supplier("partner-1", "400123");
        customer.setSupplier(false);
        when(reader.read(document)).thenReturn(invoiceData());
        when(partnerRepository.findByCompanyIdAndTaxId("company-1", "B12345678")).thenReturn(Optional.of(customer));

        InvoiceImportResult result = new InvoiceImportApplicationService(reader, journalEntryService, partnerRepository)
            .importSupplierInvoice("company-1", "factura.pdf", document);

        assertThat(result.supplierResolution()).isEqualTo(SupplierResolutionStatus.NOT_USABLE);
        assertThat(result.supplierId()).isEqualTo("partner-1");
        assertThat(result.warnings()).contains("El tercer existeix pero no es un proveidor actiu");
        verify(journalEntryService, never()).create(eq("company-1"), org.mockito.ArgumentMatchers.any());
    }

    private InvoiceDocumentData invoiceData() {
        return invoiceData("B12345678");
    }

    private InvoiceDocumentData invoiceData(String taxId) {
        return new InvoiceDocumentData(
            LocalDate.of(2026, 6, 15),
            "Proveidor",
            taxId,
            "F-19",
            new BigDecimal("100.00"),
            new BigDecimal("21.00"),
            new BigDecimal("121.00"),
            100,
            List.of()
        );
    }

    private Partner supplier(String id, String account) {
        Partner supplier = new Partner();
        supplier.setId(id);
        supplier.setSupplier(true);
        supplier.setActive(true);
        supplier.setSupplierAccount(account);
        return supplier;
    }
}
