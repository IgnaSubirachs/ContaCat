package cat.contacat.erp.sales.invoice.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import cat.contacat.erp.sales.invoice.SalesInvoice;
import cat.contacat.erp.sales.invoice.SalesInvoiceRepository;
import cat.contacat.erp.sales.invoice.SalesInvoiceStatus;
import cat.contacat.erp.sales.invoice.SalesInvoiceValidationException;
import cat.contacat.erp.sales.order.SalesOrder;
import cat.contacat.erp.sales.order.SalesOrderLine;
import cat.contacat.erp.sales.order.SalesOrderRepository;
import cat.contacat.erp.sales.order.SalesOrderStatus;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class SalesInvoiceApplicationServiceTest {

    @Mock private SalesInvoiceRepository repository;
    @Mock private SalesOrderRepository orderRepository;
    @Mock private CompanyRepository companyRepository;
    @Mock private DocumentSequenceService documentSequenceService;
    @Mock private SalesInvoiceAccountingService accountingService;

    @InjectMocks private SalesInvoiceApplicationService service;

    @Test
    void createFromDeliveredOrderCreatesUnnumberedDraft() {
        SalesOrder order = deliveredOrder();
        when(orderRepository.findById("order-1")).thenReturn(Optional.of(order));
        when(repository.existsBySalesOrderId("order-1")).thenReturn(false);
        when(repository.save(any(SalesInvoice.class))).thenAnswer(invocation -> invocation.getArgument(0));

        SalesInvoice invoice = service.createFromOrder("company-1", "order-1", LocalDate.of(2026, 6, 12), null);

        assertThat(invoice.getStatus()).isEqualTo(SalesInvoiceStatus.DRAFT);
        assertThat(invoice.getInvoiceNumber()).isNull();
        assertThat(invoice.getDueDate()).isEqualTo(LocalDate.of(2026, 7, 12));
        assertThat(invoice.getLines()).hasSize(1);
        verify(documentSequenceService, never()).allocateNext(any(), any(), any(), any(Integer.class));
    }

    @Test
    void createFromOrderRejectsOrdersNotDelivered() {
        SalesOrder order = deliveredOrder();
        order.setStatus(SalesOrderStatus.CONFIRMED);
        when(orderRepository.findById("order-1")).thenReturn(Optional.of(order));

        assertThatThrownBy(() -> service.createFromOrder("company-1", "order-1", null, null))
            .isInstanceOf(SalesInvoiceValidationException.class)
            .hasMessageContaining("lliurades");
    }

    @Test
    void createFromOrderRejectsDuplicateInvoice() {
        when(orderRepository.findById("order-1")).thenReturn(Optional.of(deliveredOrder()));
        when(repository.existsBySalesOrderId("order-1")).thenReturn(true);

        assertThatThrownBy(() -> service.createFromOrder("company-1", "order-1", null, null))
            .isInstanceOf(SalesInvoiceValidationException.class)
            .hasMessageContaining("ja te");
    }

    @Test
    void issueAllocatesDefinitiveNumber() {
        SalesInvoice invoice = draftInvoice();
        when(repository.findById("invoice-1")).thenReturn(Optional.of(invoice));
        when(documentSequenceService.allocateNext("company-1", "SALES_INVOICE", "A", 2026))
            .thenReturn(new DocumentNumber("seq-1", "company-1", "SALES_INVOICE", "A", 2026, 7, "FV-2026-00007"));
        JournalEntry entry = new JournalEntry();
        entry.setId("entry-1");
        when(accountingService.createAndPost(invoice)).thenReturn(entry);
        when(repository.save(invoice)).thenReturn(invoice);

        SalesInvoice issued = service.issue("company-1", "invoice-1");

        assertThat(issued.getStatus()).isEqualTo(SalesInvoiceStatus.ISSUED);
        assertThat(issued.getInvoiceNumber()).isEqualTo("FV-2026-00007");
        assertThat(issued.getJournalEntry()).isSameAs(entry);
        assertThat(issued.getIssuedAt()).isNotNull();
        verify(accountingService).createAndPost(invoice);
    }

    @Test
    void issuedInvoiceCannotBeDeleted() {
        SalesInvoice invoice = draftInvoice();
        invoice.setStatus(SalesInvoiceStatus.ISSUED);
        when(repository.findById("invoice-1")).thenReturn(Optional.of(invoice));

        assertThatThrownBy(() -> service.deleteDraft("company-1", "invoice-1"))
            .isInstanceOf(SalesInvoiceValidationException.class)
            .hasMessageContaining("rectificativa");
        verify(repository, never()).delete(invoice);
    }

    @Test
    void onlyIssuedInvoiceCanBeMarkedPaid() {
        SalesInvoice invoice = draftInvoice();
        when(repository.findById("invoice-1")).thenReturn(Optional.of(invoice));

        assertThatThrownBy(() -> service.markPaid("company-1", "invoice-1"))
            .isInstanceOf(SalesInvoiceValidationException.class)
            .hasMessageContaining("emeses");
    }

    private SalesInvoice draftInvoice() {
        SalesOrder order = deliveredOrder();
        SalesInvoice invoice = new SalesInvoice();
        invoice.setId("invoice-1");
        invoice.setCompany(order.getCompany());
        invoice.setPartner(order.getPartner());
        invoice.setSalesOrder(order);
        invoice.setInvoiceDate(LocalDate.of(2026, 6, 12));
        invoice.setDueDate(LocalDate.of(2026, 7, 12));
        invoice.setStatus(SalesInvoiceStatus.DRAFT);
        invoice.setLines(new ArrayList<>());
        return invoice;
    }

    private SalesOrder deliveredOrder() {
        Company company = new Company();
        company.setId("company-1");
        Partner partner = new Partner();
        partner.setId("partner-1");
        partner.setCompany(company);
        partner.setName("Client test");

        SalesOrder order = new SalesOrder();
        order.setId("order-1");
        order.setCompany(company);
        order.setPartner(partner);
        order.setOrderNumber("CV-2026-00001");
        order.setOrderDate(LocalDate.of(2026, 6, 10));
        order.setStatus(SalesOrderStatus.DELIVERED);
        order.setLines(new ArrayList<>());

        SalesOrderLine line = new SalesOrderLine();
        line.setSalesOrder(order);
        line.setLineOrder(1);
        line.setProductCode("SERV-001");
        line.setDescription("Consultoria");
        line.setQuantity(new BigDecimal("1.000"));
        line.setUnitPrice(new BigDecimal("100.00"));
        line.setDiscountPercent(BigDecimal.ZERO);
        line.setTaxRate(new BigDecimal("21.00"));
        order.getLines().add(line);
        return order;
    }
}
