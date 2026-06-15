package cat.contacat.erp.integration;

import static org.assertj.core.api.Assertions.assertThat;

import cat.contacat.erp.sales.invoice.SalesInvoice;
import cat.contacat.erp.sales.invoice.SalesInvoiceStatus;
import cat.contacat.erp.sales.invoice.application.SalesInvoiceApplicationService;
import java.math.BigDecimal;
import java.time.LocalDate;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.testcontainers.junit.jupiter.Testcontainers;

@SpringBootTest
@Testcontainers(disabledWithoutDocker = true)
class SalesInvoiceAccountingIntegrationTest extends AbstractMySqlIntegrationTest {

    private static final String COMPANY_ID = "00000000-0000-0000-0000-000000000001";
    private static final String PARTNER_ID = "10000000-0000-0000-0000-000000000001";
    private static final String ORDER_ID = "20000000-0000-0000-0000-000000000001";

    @Autowired
    private SalesInvoiceApplicationService invoiceService;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @BeforeEach
    void seedDeliveredOrder() {
        jdbcTemplate.update("""
            insert into partners (
                id, company_id, name, tax_id, email, phone, is_customer,
                contract_summary, accrual_notes, internal_notes
            )
            values (?, ?, 'Client integracio', 'B87654321', 'client@example.cat', '930000000', true, '', '', '')
            """, PARTNER_ID, COMPANY_ID);
        jdbcTemplate.update("""
            insert into sales_orders (
                id, company_id, partner_id, series, fiscal_year, sequence_number, order_number,
                order_date, status, delivery_date
            ) values (?, ?, ?, 'A', 2026, 1, 'CV-2026-TEST', '2026-06-15', 'DELIVERED', '2026-06-15')
            """, ORDER_ID, COMPANY_ID, PARTNER_ID);
        jdbcTemplate.update("""
            insert into sales_order_lines (
                id, sales_order_id, line_order, product_code, description, quantity, unit_price,
                discount_percent, tax_rate
            ) values ('30000000-0000-0000-0000-000000000001', ?, 1, 'SERV-001', 'Servei professional', 1, 100, 0, 21)
            """, ORDER_ID);
    }

    @Test
    void issuingInvoicePersistsNumberAndPostedBalancedJournalEntry() {
        SalesInvoice draft = invoiceService.createFromOrder(
            COMPANY_ID,
            ORDER_ID,
            LocalDate.of(2026, 6, 15),
            LocalDate.of(2026, 7, 15)
        );

        SalesInvoice issued = invoiceService.issue(COMPANY_ID, draft.getId());

        assertThat(issued.getStatus()).isEqualTo(SalesInvoiceStatus.ISSUED);
        assertThat(issued.getInvoiceNumber()).isEqualTo("FV-2026-00001");
        assertThat(issued.getJournalEntry()).isNotNull();

        String journalEntryId = issued.getJournalEntry().getId();
        String journalStatus = jdbcTemplate.queryForObject(
            "select status from journal_entries where id = ?",
            String.class,
            journalEntryId
        );
        BigDecimal debit = jdbcTemplate.queryForObject(
            "select sum(debit) from journal_lines where journal_entry_id = ?",
            BigDecimal.class,
            journalEntryId
        );
        BigDecimal credit = jdbcTemplate.queryForObject(
            "select sum(credit) from journal_lines where journal_entry_id = ?",
            BigDecimal.class,
            journalEntryId
        );
        String linkedEntryId = jdbcTemplate.queryForObject(
            "select journal_entry_id from sales_invoices where id = ?",
            String.class,
            issued.getId()
        );

        assertThat(journalStatus).isEqualTo("POSTED");
        assertThat(debit).isEqualByComparingTo("121.00");
        assertThat(credit).isEqualByComparingTo("121.00");
        assertThat(linkedEntryId).isEqualTo(journalEntryId);
    }
}
