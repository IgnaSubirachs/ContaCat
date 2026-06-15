package cat.contacat.erp.sales.invoice.application;

import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import cat.contacat.erp.core.journal.application.JournalLineCommand;
import cat.contacat.erp.sales.invoice.SalesInvoice;
import cat.contacat.erp.sales.invoice.SalesInvoiceLine;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class SalesInvoiceAccountingService {

    private static final BigDecimal ONE_HUNDRED = new BigDecimal("100.00");

    private final JournalEntryApplicationService journalEntryService;

    public SalesInvoiceAccountingService(JournalEntryApplicationService journalEntryService) {
        this.journalEntryService = journalEntryService;
    }

    public JournalEntry createAndPost(SalesInvoice invoice) {
        InvoiceTotals totals = calculateTotals(invoice.getLines());
        String description = "Factura de venda " + invoice.getInvoiceNumber() + " - " + invoice.getPartner().getName();
        List<JournalLineCommand> lines = new ArrayList<>();
        lines.add(new JournalLineCommand("430000", totals.total(), BigDecimal.ZERO, description));
        lines.add(new JournalLineCommand("700000", BigDecimal.ZERO, totals.subtotal(), description));
        if (totals.tax().compareTo(BigDecimal.ZERO) > 0) {
            lines.add(new JournalLineCommand("477000", BigDecimal.ZERO, totals.tax(), description));
        }

        JournalEntry entry = journalEntryService.create(
            invoice.getCompany().getId(),
            new JournalEntryCommand(invoice.getInvoiceDate(), description, null, lines)
        );
        return journalEntryService.post(invoice.getCompany().getId(), entry.getId());
    }

    private InvoiceTotals calculateTotals(List<SalesInvoiceLine> lines) {
        BigDecimal subtotal = lines.stream()
            .map(this::lineBase)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .setScale(2, RoundingMode.HALF_UP);
        BigDecimal tax = lines.stream()
            .map(this::lineTax)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
            .setScale(2, RoundingMode.HALF_UP);
        return new InvoiceTotals(subtotal, tax, subtotal.add(tax).setScale(2, RoundingMode.HALF_UP));
    }

    private BigDecimal lineBase(SalesInvoiceLine line) {
        BigDecimal gross = line.getQuantity().multiply(line.getUnitPrice());
        BigDecimal discount = gross.multiply(line.getDiscountPercent()).divide(ONE_HUNDRED, 2, RoundingMode.HALF_UP);
        return gross.subtract(discount).setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal lineTax(SalesInvoiceLine line) {
        return lineBase(line).multiply(line.getTaxRate()).divide(ONE_HUNDRED, 2, RoundingMode.HALF_UP);
    }

    private record InvoiceTotals(BigDecimal subtotal, BigDecimal tax, BigDecimal total) {
    }
}
