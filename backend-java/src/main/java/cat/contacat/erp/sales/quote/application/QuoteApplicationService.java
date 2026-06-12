package cat.contacat.erp.sales.quote.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.partner.PartnerNotFoundException;
import cat.contacat.erp.core.partner.PartnerRepository;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import cat.contacat.erp.sales.quote.Quote;
import cat.contacat.erp.sales.quote.QuoteLine;
import cat.contacat.erp.sales.quote.QuoteNotFoundException;
import cat.contacat.erp.sales.quote.QuoteRepository;
import cat.contacat.erp.sales.quote.QuoteStatus;
import cat.contacat.erp.sales.quote.QuoteValidationException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class QuoteApplicationService {

    private final QuoteRepository repository;
    private final CompanyRepository companyRepository;
    private final PartnerRepository partnerRepository;
    private final DocumentSequenceService documentSequenceService;

    public QuoteApplicationService(
        QuoteRepository repository,
        CompanyRepository companyRepository,
        PartnerRepository partnerRepository,
        DocumentSequenceService documentSequenceService
    ) {
        this.repository = repository;
        this.companyRepository = companyRepository;
        this.partnerRepository = partnerRepository;
        this.documentSequenceService = documentSequenceService;
    }

    @Transactional(readOnly = true)
    public List<Quote> list(String companyId, String status, LocalDate startDate, LocalDate endDate) {
        ensureCompanyExists(companyId);
        if (startDate != null && endDate != null) {
            return repository.findAllByCompanyIdAndQuoteDateBetweenOrderByQuoteDateDescQuoteNumberDesc(companyId, startDate, endDate);
        }
        QuoteStatus normalizedStatus = normalizeStatus(status, false);
        return normalizedStatus == null
            ? repository.findAllByCompanyIdOrderByQuoteDateDescQuoteNumberDesc(companyId)
            : repository.findAllByCompanyIdAndStatusOrderByQuoteDateDescQuoteNumberDesc(companyId, normalizedStatus);
    }

    @Transactional(readOnly = true)
    public Quote get(String companyId, String quoteId) {
        return findQuote(companyId, quoteId);
    }

    @Transactional
    public Quote create(String companyId, QuoteCommand command) {
        validateCommand(command);
        Company company = findCompany(companyId);
        Partner partner = findCustomerPartner(companyId, command.partnerId());
        String normalizedSeries = normalizeSeries(command.series());
        DocumentNumber allocated = documentSequenceService.allocateNext(companyId, "QUOTE", normalizedSeries, command.quoteDate().getYear());

        Quote quote = new Quote();
        quote.setCompany(company);
        quote.setPartner(partner);
        quote.setSeries(allocated.series());
        quote.setFiscalYear(allocated.fiscalYear());
        quote.setSequenceNumber(allocated.number());
        quote.setQuoteNumber(allocated.formattedNumber());
        quote.setQuoteDate(command.quoteDate());
        quote.setValidUntil(command.validUntil());
        quote.setStatus(QuoteStatus.DRAFT);
        quote.setNotes(normalizeNullable(command.notes()));
        quote.setLines(buildLines(quote, command.lines()));

        return repository.save(quote);
    }

    @Transactional
    public Quote update(String companyId, String quoteId, QuoteCommand command) {
        validateCommand(command);
        Quote quote = findQuote(companyId, quoteId);
        ensureDraft(quote, "Nomes es poden editar pressupostos en esborrany");
        Partner partner = findCustomerPartner(companyId, command.partnerId());

        quote.setPartner(partner);
        quote.setQuoteDate(command.quoteDate());
        quote.setValidUntil(command.validUntil());
        quote.setNotes(normalizeNullable(command.notes()));
        quote.getLines().clear();
        quote.getLines().addAll(buildLines(quote, command.lines()));

        return repository.save(quote);
    }

    @Transactional
    public Quote send(String companyId, String quoteId) {
        Quote quote = findQuote(companyId, quoteId);
        ensureDraft(quote, "Nomes es poden enviar pressupostos en esborrany");
        if (quote.getValidUntil().isBefore(LocalDate.now())) {
            throw new QuoteValidationException("No es pot enviar un pressupost caducat");
        }
        quote.setStatus(QuoteStatus.SENT);
        return repository.save(quote);
    }

    @Transactional
    public Quote accept(String companyId, String quoteId) {
        Quote quote = findQuote(companyId, quoteId);
        if (quote.getStatus() != QuoteStatus.DRAFT && quote.getStatus() != QuoteStatus.SENT) {
            throw new QuoteValidationException("Nomes es poden acceptar pressupostos en esborrany o enviats");
        }
        if (quote.getValidUntil().isBefore(LocalDate.now())) {
            quote.setStatus(QuoteStatus.EXPIRED);
            repository.save(quote);
            throw new QuoteValidationException("No es pot acceptar un pressupost caducat");
        }
        quote.setStatus(QuoteStatus.ACCEPTED);
        return repository.save(quote);
    }

    @Transactional
    public Quote reject(String companyId, String quoteId) {
        Quote quote = findQuote(companyId, quoteId);
        if (quote.getStatus() != QuoteStatus.DRAFT && quote.getStatus() != QuoteStatus.SENT) {
            throw new QuoteValidationException("Nomes es poden rebutjar pressupostos en esborrany o enviats");
        }
        quote.setStatus(QuoteStatus.REJECTED);
        return repository.save(quote);
    }

    @Transactional
    public void delete(String companyId, String quoteId) {
        Quote quote = findQuote(companyId, quoteId);
        ensureDraft(quote, "Nomes es poden eliminar pressupostos en esborrany");
        repository.delete(quote);
    }

    private Quote findQuote(String companyId, String quoteId) {
        Quote quote = repository.findById(quoteId)
            .orElseThrow(() -> new QuoteNotFoundException(companyId, quoteId));
        if (!Objects.equals(quote.getCompany().getId(), companyId)) {
            throw new QuoteNotFoundException(companyId, quoteId);
        }
        return quote;
    }

    private Company findCompany(String companyId) {
        return companyRepository.findById(companyId)
            .orElseThrow(() -> new CompanyNotFoundException(companyId));
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new CompanyNotFoundException(companyId);
        }
    }

    private Partner findCustomerPartner(String companyId, String partnerId) {
        Partner partner = partnerRepository.findById(partnerId)
            .orElseThrow(() -> new PartnerNotFoundException(companyId, partnerId));
        if (!Objects.equals(partner.getCompany().getId(), companyId)) {
            throw new PartnerNotFoundException(companyId, partnerId);
        }
        if (!partner.isCustomer()) {
            throw new QuoteValidationException("El partner del pressupost ha de ser un client");
        }
        if (!partner.isActive()) {
            throw new QuoteValidationException("No es pot fer un pressupost per a un client inactiu");
        }
        return partner;
    }

    private List<QuoteLine> buildLines(Quote quote, List<QuoteLineCommand> commands) {
        List<QuoteLine> lines = new ArrayList<>();
        int lineOrder = 1;
        for (QuoteLineCommand command : commands) {
            validateLine(command);
            QuoteLine line = new QuoteLine();
            line.setQuote(quote);
            line.setLineOrder(lineOrder++);
            line.setProductCode(command.productCode().trim().toUpperCase(Locale.ROOT));
            line.setDescription(command.description().trim());
            line.setQuantity(scale(command.quantity(), 3));
            line.setUnitPrice(scale(command.unitPrice(), 2));
            line.setDiscountPercent(scale(defaultZero(command.discountPercent()), 2));
            line.setTaxRate(scale(defaultTax(command.taxRate()), 2));
            lines.add(line);
        }
        return lines;
    }

    private void validateCommand(QuoteCommand command) {
        if (command.partnerId() == null || command.partnerId().isBlank()) {
            throw new QuoteValidationException("El client es obligatori");
        }
        if (command.quoteDate() == null) {
            throw new QuoteValidationException("La data del pressupost es obligatoria");
        }
        if (command.validUntil() == null) {
            throw new QuoteValidationException("La data de validesa es obligatoria");
        }
        if (command.validUntil().isBefore(command.quoteDate())) {
            throw new QuoteValidationException("La data de validesa no pot ser anterior a la data del pressupost");
        }
        if (command.lines() == null || command.lines().isEmpty()) {
            throw new QuoteValidationException("El pressupost ha de tenir almenys una linia");
        }
    }

    private void validateLine(QuoteLineCommand command) {
        if (command.productCode() == null || command.productCode().isBlank()) {
            throw new QuoteValidationException("Cada linia ha de tenir un codi de producte");
        }
        if (command.description() == null || command.description().isBlank()) {
            throw new QuoteValidationException("Cada linia ha de tenir descripcio");
        }
        if (command.quantity() == null || command.quantity().compareTo(BigDecimal.ZERO) <= 0) {
            throw new QuoteValidationException("La quantitat de la linia ha de ser superior a 0");
        }
        if (command.unitPrice() == null || command.unitPrice().compareTo(BigDecimal.ZERO) < 0) {
            throw new QuoteValidationException("El preu unitari no pot ser negatiu");
        }
        BigDecimal discount = defaultZero(command.discountPercent());
        if (discount.compareTo(BigDecimal.ZERO) < 0 || discount.compareTo(new BigDecimal("100.00")) > 0) {
            throw new QuoteValidationException("El descompte de la linia ha d'estar entre 0 i 100");
        }
        BigDecimal taxRate = defaultTax(command.taxRate());
        if (taxRate.compareTo(BigDecimal.ZERO) < 0) {
            throw new QuoteValidationException("El tipus d'impost de la linia no pot ser negatiu");
        }
    }

    private QuoteStatus normalizeStatus(String status, boolean required) {
        if (status == null || status.isBlank()) {
            if (required) {
                throw new QuoteValidationException("L'estat del pressupost es obligatori");
            }
            return null;
        }
        try {
            return QuoteStatus.valueOf(status.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException exception) {
            throw new QuoteValidationException("L'estat del pressupost no es valid");
        }
    }

    private String normalizeSeries(String series) {
        return series == null || series.isBlank() ? "A" : series.trim().toUpperCase(Locale.ROOT);
    }

    private void ensureDraft(Quote quote, String message) {
        if (quote.getStatus() != QuoteStatus.DRAFT) {
            throw new QuoteValidationException(message);
        }
    }

    private BigDecimal defaultZero(BigDecimal value) {
        return value == null ? BigDecimal.ZERO : value;
    }

    private BigDecimal defaultTax(BigDecimal value) {
        return value == null ? new BigDecimal("21.00") : value;
    }

    private BigDecimal scale(BigDecimal value, int scale) {
        return value.setScale(scale, RoundingMode.HALF_UP);
    }

    private String normalizeNullable(String value) {
        return value == null || value.isBlank() ? null : value.trim();
    }
}
