package cat.contacat.erp.core.journal.importer;

import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import cat.contacat.erp.core.journal.application.JournalLineCommand;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.partner.PartnerRepository;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class InvoiceImportApplicationService {

    private final InvoiceDocumentReader reader;
    private final JournalEntryApplicationService journalEntryService;
    private final PartnerRepository partnerRepository;

    public InvoiceImportApplicationService(
        InvoiceDocumentReader reader,
        JournalEntryApplicationService journalEntryService,
        PartnerRepository partnerRepository
    ) {
        this.reader = reader;
        this.journalEntryService = journalEntryService;
        this.partnerRepository = partnerRepository;
    }

    @Transactional
    public InvoiceImportResult importSupplierInvoice(String companyId, String filename, byte[] document) {
        InvoiceDocumentData data = reader.read(document);
        List<String> warnings = new ArrayList<>(data.warnings());
        if (data.supplierTaxId() == null || data.supplierTaxId().isBlank()) {
            warnings.add("No es pot cercar el proveidor sense NIF/CIF");
            return unresolved(data, null, SupplierResolutionStatus.TAX_ID_NOT_DETECTED, warnings);
        }
        Optional<Partner> supplier = findSupplier(companyId, data.supplierTaxId());
        if (supplier.isEmpty()) {
            warnings.add("Proveidor no trobat; cal crear-lo abans de generar l'assentament");
            return unresolved(data, null, SupplierResolutionStatus.NOT_FOUND, warnings);
        }
        if (!supplier.get().isSupplier() || !supplier.get().isActive()) {
            warnings.add("El tercer existeix pero no es un proveidor actiu");
            return unresolved(data, supplier.get().getId(), SupplierResolutionStatus.NOT_USABLE, warnings);
        }

        Partner resolvedSupplier = supplier.get();
        String description = data.invoiceNumber() == null
            ? "Factura de proveidor importada"
            : "Factura de proveidor " + data.invoiceNumber();
        if (data.supplierName() != null) {
            description += " - " + data.supplierName();
        }
        List<JournalLineCommand> lines = new ArrayList<>();
        lines.add(new JournalLineCommand("600000", data.taxableBase(), BigDecimal.ZERO, description));
        if (data.taxAmount().compareTo(BigDecimal.ZERO) > 0) {
            lines.add(new JournalLineCommand("472000", data.taxAmount(), BigDecimal.ZERO, "IVA suportat"));
        }
        lines.add(new JournalLineCommand(supplierAccount(resolvedSupplier, warnings), BigDecimal.ZERO, data.total(), description));

        JournalEntry draft = journalEntryService.create(
            companyId,
            new JournalEntryCommand(data.invoiceDate(), description, filename, lines)
        );
        return new InvoiceImportResult(
            draft,
            data.supplierName(),
            data.supplierTaxId(),
            resolvedSupplier.getId(),
            SupplierResolutionStatus.FOUND,
            data.confidence(),
            List.copyOf(warnings)
        );
    }

    private Optional<Partner> findSupplier(String companyId, String taxId) {
        return partnerRepository.findByCompanyIdAndTaxId(companyId, taxId.trim().toUpperCase(Locale.ROOT));
    }

    private String supplierAccount(Partner supplier, List<String> warnings) {
        if (supplier.getSupplierAccount() == null || supplier.getSupplierAccount().isBlank()) {
            warnings.add("El proveidor no te compte comptable configurat; s'ha utilitzat el compte 400000");
            return "400000";
        }
        return supplier.getSupplierAccount();
    }

    private InvoiceImportResult unresolved(
        InvoiceDocumentData data,
        String supplierId,
        SupplierResolutionStatus status,
        List<String> warnings
    ) {
        return new InvoiceImportResult(
            null,
            data.supplierName(),
            data.supplierTaxId(),
            supplierId,
            status,
            data.confidence(),
            List.copyOf(warnings)
        );
    }
}
