package cat.contacat.erp.sales.invoice.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.journal.application.JournalEntryApplicationService;
import cat.contacat.erp.core.journal.application.JournalEntryCommand;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.sales.invoice.SalesInvoice;
import cat.contacat.erp.sales.invoice.SalesInvoiceLine;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class SalesInvoiceAccountingServiceTest {

    @Mock private JournalEntryApplicationService journalEntryService;

    @Test
    void createsAndPostsBalancedJournalEntry() {
        SalesInvoice invoice = invoice();
        JournalEntry draftEntry = new JournalEntry();
        draftEntry.setId("entry-1");
        JournalEntry postedEntry = new JournalEntry();
        postedEntry.setId("entry-1");
        when(journalEntryService.create(eq("company-1"), any())).thenReturn(draftEntry);
        when(journalEntryService.post("company-1", "entry-1")).thenReturn(postedEntry);

        JournalEntry result = new SalesInvoiceAccountingService(journalEntryService).createAndPost(invoice);

        ArgumentCaptor<JournalEntryCommand> command = ArgumentCaptor.forClass(JournalEntryCommand.class);
        verify(journalEntryService).create(eq("company-1"), command.capture());
        verify(journalEntryService).post("company-1", "entry-1");
        assertThat(result).isSameAs(postedEntry);
        assertThat(command.getValue().lines()).hasSize(3);
        assertThat(command.getValue().lines().get(0).debit()).isEqualByComparingTo("121.00");
        assertThat(command.getValue().lines().get(1).credit()).isEqualByComparingTo("100.00");
        assertThat(command.getValue().lines().get(2).credit()).isEqualByComparingTo("21.00");
    }

    private SalesInvoice invoice() {
        Company company = new Company();
        company.setId("company-1");
        Partner partner = new Partner();
        partner.setName("Client test");

        SalesInvoice invoice = new SalesInvoice();
        invoice.setCompany(company);
        invoice.setPartner(partner);
        invoice.setInvoiceNumber("FV-2026-00001");
        invoice.setInvoiceDate(LocalDate.of(2026, 6, 15));

        SalesInvoiceLine line = new SalesInvoiceLine();
        line.setQuantity(new BigDecimal("1.000"));
        line.setUnitPrice(new BigDecimal("100.00"));
        line.setDiscountPercent(BigDecimal.ZERO);
        line.setTaxRate(new BigDecimal("21.00"));
        invoice.setLines(List.of(line));
        return invoice;
    }
}
