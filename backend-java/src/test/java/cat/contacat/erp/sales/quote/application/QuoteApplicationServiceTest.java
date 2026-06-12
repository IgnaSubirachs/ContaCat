package cat.contacat.erp.sales.quote.application;

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
import cat.contacat.erp.sales.quote.Quote;
import cat.contacat.erp.sales.quote.QuoteNotFoundException;
import cat.contacat.erp.sales.quote.QuoteRepository;
import cat.contacat.erp.sales.quote.QuoteStatus;
import cat.contacat.erp.sales.quote.QuoteValidationException;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class QuoteApplicationServiceTest {

    @Mock
    private QuoteRepository repository;

    @Mock
    private CompanyRepository companyRepository;

    @Mock
    private PartnerRepository partnerRepository;

    @Mock
    private DocumentSequenceService documentSequenceService;

    @InjectMocks
    private QuoteApplicationService service;

    @Test
    void createAllocatesSequenceAndPersistsDraftQuote() {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        QuoteCommand command = quoteCommand("partner-1");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(partnerRepository.findById("partner-1")).thenReturn(Optional.of(partner));
        when(documentSequenceService.allocateNext("company-1", "QUOTE", "A", 2026))
            .thenReturn(new DocumentNumber("seq-1", "company-1", "QUOTE", "A", 2026, 7, "PR-2026-00007"));
        when(repository.save(any(Quote.class))).thenAnswer(invocation -> {
            Quote quote = invocation.getArgument(0);
            quote.setId("quote-1");
            return quote;
        });

        Quote quote = service.create("company-1", command);

        assertThat(quote.getId()).isEqualTo("quote-1");
        assertThat(quote.getQuoteNumber()).isEqualTo("PR-2026-00007");
        assertThat(quote.getStatus()).isEqualTo(QuoteStatus.DRAFT);
        assertThat(quote.getLines()).hasSize(1);
    }

    @Test
    void createFailsWhenPartnerIsNotCustomer() {
        Company company = company("company-1");
        Partner partner = supplierOnly(company, "partner-1");

        when(companyRepository.findById("company-1")).thenReturn(Optional.of(company));
        when(partnerRepository.findById("partner-1")).thenReturn(Optional.of(partner));

        assertThatThrownBy(() -> service.create("company-1", quoteCommand("partner-1")))
            .isInstanceOf(QuoteValidationException.class)
            .hasMessageContaining("client");
    }

    @Test
    void updateFailsWhenQuoteIsNotDraft() {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        Quote quote = existingQuote(company, partner, QuoteStatus.SENT);

        when(repository.findById("quote-1")).thenReturn(Optional.of(quote));

        assertThatThrownBy(() -> service.update("company-1", "quote-1", quoteCommand("partner-1")))
            .isInstanceOf(QuoteValidationException.class)
            .hasMessageContaining("esborrany");
    }

    @Test
    void sendMovesDraftQuoteToSent() {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        Quote quote = existingQuote(company, partner, QuoteStatus.DRAFT);

        when(repository.findById("quote-1")).thenReturn(Optional.of(quote));
        when(repository.save(quote)).thenReturn(quote);

        Quote response = service.send("company-1", "quote-1");

        assertThat(response.getStatus()).isEqualTo(QuoteStatus.SENT);
    }

    @Test
    void acceptDraftQuoteMarksItAccepted() {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        Quote quote = existingQuote(company, partner, QuoteStatus.DRAFT);

        when(repository.findById("quote-1")).thenReturn(Optional.of(quote));
        when(repository.save(quote)).thenReturn(quote);

        Quote response = service.accept("company-1", "quote-1");

        assertThat(response.getStatus()).isEqualTo(QuoteStatus.ACCEPTED);
    }

    @Test
    void deleteDraftRemovesQuote() {
        Company company = company("company-1");
        Partner partner = customer(company, "partner-1");
        Quote quote = existingQuote(company, partner, QuoteStatus.DRAFT);

        when(repository.findById("quote-1")).thenReturn(Optional.of(quote));

        service.delete("company-1", "quote-1");

        verify(repository).delete(quote);
    }

    @Test
    void getFailsWhenQuoteBelongsToAnotherCompany() {
        Company company = company("company-2");
        Partner partner = customer(company, "partner-1");
        Quote quote = existingQuote(company, partner, QuoteStatus.DRAFT);

        when(repository.findById("quote-1")).thenReturn(Optional.of(quote));

        assertThatThrownBy(() -> service.get("company-1", "quote-1"))
            .isInstanceOf(QuoteNotFoundException.class);
    }

    private QuoteCommand quoteCommand(String partnerId) {
        return new QuoteCommand(
            partnerId,
            "a",
            LocalDate.of(2026, 6, 12),
            LocalDate.of(2026, 7, 12),
            "Observacions",
            List.of(new QuoteLineCommand("serv-001", "Consultoria", new BigDecimal("2.000"), new BigDecimal("150.00"), new BigDecimal("10.00"), new BigDecimal("21.00")))
        );
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
        partner.setSupplier(false);
        partner.setActive(true);
        partner.setName("Client test");
        return partner;
    }

    private Partner supplierOnly(Company company, String id) {
        Partner partner = customer(company, id);
        partner.setCustomer(false);
        partner.setSupplier(true);
        return partner;
    }

    private Quote existingQuote(Company company, Partner partner, QuoteStatus status) {
        Quote quote = new Quote();
        quote.setId("quote-1");
        quote.setCompany(company);
        quote.setPartner(partner);
        quote.setSeries("A");
        quote.setFiscalYear(2026);
        quote.setSequenceNumber(1);
        quote.setQuoteNumber("PR-2026-00001");
        quote.setQuoteDate(LocalDate.of(2026, 6, 12));
        quote.setValidUntil(LocalDate.now().plusDays(10));
        quote.setStatus(status);
        quote.setLines(new java.util.ArrayList<>());
        quote.getLines().add(serviceLine(quote));
        return quote;
    }

    private cat.contacat.erp.sales.quote.QuoteLine serviceLine(Quote quote) {
        cat.contacat.erp.sales.quote.QuoteLine line = new cat.contacat.erp.sales.quote.QuoteLine();
        line.setQuote(quote);
        line.setLineOrder(1);
        line.setProductCode("SERV-001");
        line.setDescription("Consultoria");
        line.setQuantity(new BigDecimal("1.000"));
        line.setUnitPrice(new BigDecimal("100.00"));
        line.setDiscountPercent(BigDecimal.ZERO);
        line.setTaxRate(new BigDecimal("21.00"));
        return line;
    }
}
