package cat.contacat.erp.sales.order.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.partner.PartnerRepository;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import cat.contacat.erp.sales.order.SalesOrder;
import cat.contacat.erp.sales.order.SalesOrderRepository;
import cat.contacat.erp.sales.order.SalesOrderStatus;
import cat.contacat.erp.sales.order.SalesOrderValidationException;
import cat.contacat.erp.sales.quote.Quote;
import cat.contacat.erp.sales.quote.QuoteLine;
import cat.contacat.erp.sales.quote.QuoteRepository;
import cat.contacat.erp.sales.quote.QuoteStatus;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class SalesOrderApplicationServiceTest {

    @Mock private SalesOrderRepository repository;
    @Mock private CompanyRepository companyRepository;
    @Mock private PartnerRepository partnerRepository;
    @Mock private QuoteRepository quoteRepository;
    @Mock private DocumentSequenceService documentSequenceService;

    @InjectMocks private SalesOrderApplicationService service;

    @Test
    void createFromQuoteCreatesDraftOrderWithCopiedLines() {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        Quote quote = acceptedQuote(company, partner);

        when(quoteRepository.findById("quote-1")).thenReturn(Optional.of(quote));
        when(documentSequenceService.allocateNext("company-1", "SALES_ORDER", "A", 2026))
            .thenReturn(new DocumentNumber("seq-1", "company-1", "SALES_ORDER", "A", 2026, 3, "CV-2026-00003"));
        when(repository.save(any(SalesOrder.class))).thenAnswer(invocation -> {
            SalesOrder order = invocation.getArgument(0);
            order.setId("order-1");
            return order;
        });

        SalesOrder order = service.createFromQuote("company-1", "quote-1", LocalDate.of(2026, 6, 12));

        assertThat(order.getId()).isEqualTo("order-1");
        assertThat(order.getOrderNumber()).isEqualTo("CV-2026-00003");
        assertThat(order.getStatus()).isEqualTo(SalesOrderStatus.DRAFT);
        assertThat(order.getLines()).hasSize(1);
        assertThat(order.getQuote().getId()).isEqualTo("quote-1");
    }

    @Test
    void createFromQuoteFailsWhenQuoteNotAccepted() {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        Quote quote = acceptedQuote(company, partner);
        quote.setStatus(QuoteStatus.SENT);

        when(quoteRepository.findById("quote-1")).thenReturn(Optional.of(quote));

        assertThatThrownBy(() -> service.createFromQuote("company-1", "quote-1", LocalDate.of(2026, 6, 12)))
            .isInstanceOf(SalesOrderValidationException.class)
            .hasMessageContaining("acceptats");
    }

    @Test
    void confirmMovesDraftToConfirmed() {
        SalesOrder order = existingOrder(SalesOrderStatus.DRAFT);
        when(repository.findById("order-1")).thenReturn(Optional.of(order));
        when(repository.save(order)).thenReturn(order);

        SalesOrder response = service.confirm("company-1", "order-1");

        assertThat(response.getStatus()).isEqualTo(SalesOrderStatus.CONFIRMED);
    }

    @Test
    void deliverMovesConfirmedToDelivered() {
        SalesOrder order = existingOrder(SalesOrderStatus.CONFIRMED);
        when(repository.findById("order-1")).thenReturn(Optional.of(order));
        when(repository.save(order)).thenReturn(order);

        SalesOrder response = service.deliver("company-1", "order-1");

        assertThat(response.getStatus()).isEqualTo(SalesOrderStatus.DELIVERED);
        assertThat(response.getDeliveryDate()).isNotNull();
    }

    @Test
    void cancelFailsWhenOrderAlreadyDelivered() {
        SalesOrder order = existingOrder(SalesOrderStatus.DELIVERED);
        when(repository.findById("order-1")).thenReturn(Optional.of(order));

        assertThatThrownBy(() -> service.cancel("company-1", "order-1"))
            .isInstanceOf(SalesOrderValidationException.class);
    }

    @Test
    void cancelMarksNonDeliveredOrderCancelled() {
        SalesOrder order = existingOrder(SalesOrderStatus.CONFIRMED);
        when(repository.findById("order-1")).thenReturn(Optional.of(order));
        when(repository.save(order)).thenReturn(order);

        SalesOrder response = service.cancel("company-1", "order-1");

        assertThat(response.getStatus()).isEqualTo(SalesOrderStatus.CANCELLED);
        verify(repository).save(order);
    }

    private Company company(String id) {
        Company company = new Company();
        company.setId(id);
        return company;
    }

    private Partner customer(Company company, String id) {
        Partner partner = new Partner();
        partner.setId(id);
        partner.setCompany(company);
        partner.setCustomer(true);
        partner.setActive(true);
        partner.setName("Client test");
        return partner;
    }

    private Quote acceptedQuote(Company company, Partner partner) {
        Quote quote = new Quote();
        quote.setId("quote-1");
        quote.setCompany(company);
        quote.setPartner(partner);
        quote.setQuoteNumber("PR-2026-00001");
        quote.setQuoteDate(LocalDate.of(2026, 6, 10));
        quote.setValidUntil(LocalDate.of(2026, 7, 10));
        quote.setStatus(QuoteStatus.ACCEPTED);
        quote.setLines(new ArrayList<>());
        QuoteLine line = new QuoteLine();
        line.setQuote(quote);
        line.setLineOrder(1);
        line.setProductCode("SERV-001");
        line.setDescription("Consultoria");
        line.setQuantity(new BigDecimal("1.000"));
        line.setUnitPrice(new BigDecimal("100.00"));
        line.setDiscountPercent(BigDecimal.ZERO);
        line.setTaxRate(new BigDecimal("21.00"));
        quote.getLines().add(line);
        return quote;
    }

    private SalesOrder existingOrder(SalesOrderStatus status) {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        SalesOrder order = new SalesOrder();
        order.setId("order-1");
        order.setCompany(company);
        order.setPartner(partner);
        order.setOrderDate(LocalDate.of(2026, 6, 12));
        order.setOrderNumber("CV-2026-00001");
        order.setStatus(status);
        order.setLines(List.of());
        return order;
    }
}
