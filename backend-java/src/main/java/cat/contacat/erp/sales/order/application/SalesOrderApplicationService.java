package cat.contacat.erp.sales.order.application;

import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.core.partner.PartnerNotFoundException;
import cat.contacat.erp.core.partner.PartnerRepository;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import cat.contacat.erp.sales.order.SalesOrder;
import cat.contacat.erp.sales.order.SalesOrderLine;
import cat.contacat.erp.sales.order.SalesOrderNotFoundException;
import cat.contacat.erp.sales.order.SalesOrderRepository;
import cat.contacat.erp.sales.order.SalesOrderStatus;
import cat.contacat.erp.sales.order.SalesOrderValidationException;
import cat.contacat.erp.sales.quote.Quote;
import cat.contacat.erp.sales.quote.QuoteNotFoundException;
import cat.contacat.erp.sales.quote.QuoteRepository;
import cat.contacat.erp.sales.quote.QuoteStatus;
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
public class SalesOrderApplicationService {

    private final SalesOrderRepository repository;
    private final CompanyRepository companyRepository;
    private final PartnerRepository partnerRepository;
    private final QuoteRepository quoteRepository;
    private final DocumentSequenceService documentSequenceService;

    public SalesOrderApplicationService(
        SalesOrderRepository repository,
        CompanyRepository companyRepository,
        PartnerRepository partnerRepository,
        QuoteRepository quoteRepository,
        DocumentSequenceService documentSequenceService
    ) {
        this.repository = repository;
        this.companyRepository = companyRepository;
        this.partnerRepository = partnerRepository;
        this.quoteRepository = quoteRepository;
        this.documentSequenceService = documentSequenceService;
    }

    @Transactional(readOnly = true)
    public List<SalesOrder> list(String companyId, String status) {
        ensureCompanyExists(companyId);
        SalesOrderStatus normalizedStatus = normalizeStatus(status, false);
        return normalizedStatus == null
            ? repository.findAllByCompanyIdOrderByOrderDateDescOrderNumberDesc(companyId)
            : repository.findAllByCompanyIdAndStatusOrderByOrderDateDescOrderNumberDesc(companyId, normalizedStatus);
    }

    @Transactional(readOnly = true)
    public SalesOrder get(String companyId, String orderId) {
        return findOrder(companyId, orderId);
    }

    @Transactional
    public SalesOrder create(String companyId, SalesOrderCommand command) {
        validateCommand(command);
        Company company = findCompany(companyId);
        Partner partner = findCustomerPartner(companyId, command.partnerId());
        DocumentNumber allocated = documentSequenceService.allocateNext(companyId, "SALES_ORDER", normalizeSeries(command.series()), command.orderDate().getYear());

        SalesOrder order = new SalesOrder();
        order.setCompany(company);
        order.setPartner(partner);
        order.setSeries(allocated.series());
        order.setFiscalYear(allocated.fiscalYear());
        order.setSequenceNumber(allocated.number());
        order.setOrderNumber(allocated.formattedNumber());
        order.setOrderDate(command.orderDate());
        order.setDeliveryDate(command.deliveryDate());
        order.setDeliveryAddress(normalizeNullable(command.deliveryAddress()));
        order.setNotes(normalizeNullable(command.notes()));
        order.setStatus(SalesOrderStatus.DRAFT);
        order.setLines(buildLines(order, command.lines()));
        return repository.save(order);
    }

    @Transactional
    public SalesOrder update(String companyId, String orderId, SalesOrderCommand command) {
        validateCommand(command);
        SalesOrder order = findOrder(companyId, orderId);
        if (order.getStatus() != SalesOrderStatus.DRAFT) {
            throw new SalesOrderValidationException("Nomes es poden editar comandes en esborrany");
        }
        Partner partner = findCustomerPartner(companyId, command.partnerId());
        order.setPartner(partner);
        order.setOrderDate(command.orderDate());
        order.setDeliveryDate(command.deliveryDate());
        order.setDeliveryAddress(normalizeNullable(command.deliveryAddress()));
        order.setNotes(normalizeNullable(command.notes()));
        order.getLines().clear();
        order.getLines().addAll(buildLines(order, command.lines()));
        return repository.save(order);
    }

    @Transactional
    public SalesOrder createFromQuote(String companyId, String quoteId, LocalDate orderDate) {
        Quote quote = quoteRepository.findById(quoteId)
            .orElseThrow(() -> new QuoteNotFoundException(companyId, quoteId));
        if (!Objects.equals(quote.getCompany().getId(), companyId)) {
            throw new QuoteNotFoundException(companyId, quoteId);
        }
        if (quote.getStatus() != QuoteStatus.ACCEPTED) {
            throw new SalesOrderValidationException("Nomes es poden convertir pressupostos acceptats");
        }
        DocumentNumber allocated = documentSequenceService.allocateNext(companyId, "SALES_ORDER", "A", effectiveDate(orderDate).getYear());

        SalesOrder order = new SalesOrder();
        order.setCompany(quote.getCompany());
        order.setPartner(quote.getPartner());
        order.setQuote(quote);
        order.setSeries(allocated.series());
        order.setFiscalYear(allocated.fiscalYear());
        order.setSequenceNumber(allocated.number());
        order.setOrderNumber(allocated.formattedNumber());
        order.setOrderDate(effectiveDate(orderDate));
        order.setDeliveryAddress(normalizeNullable(quote.getPartner().getAddressStreet()));
        order.setNotes(normalizeNullable(quote.getNotes()));
        order.setStatus(SalesOrderStatus.DRAFT);
        order.setLines(copyLines(order, quote));
        return repository.save(order);
    }

    @Transactional
    public SalesOrder confirm(String companyId, String orderId) {
        SalesOrder order = findOrder(companyId, orderId);
        if (order.getStatus() != SalesOrderStatus.DRAFT) {
            throw new SalesOrderValidationException("Nomes es poden confirmar comandes en esborrany");
        }
        order.setStatus(SalesOrderStatus.CONFIRMED);
        return repository.save(order);
    }

    @Transactional
    public SalesOrder deliver(String companyId, String orderId) {
        SalesOrder order = findOrder(companyId, orderId);
        if (order.getStatus() != SalesOrderStatus.CONFIRMED && order.getStatus() != SalesOrderStatus.IN_PROGRESS) {
            throw new SalesOrderValidationException("Nomes es poden lliurar comandes confirmades o en proces");
        }
        order.setStatus(SalesOrderStatus.DELIVERED);
        if (order.getDeliveryDate() == null) {
            order.setDeliveryDate(LocalDate.now());
        }
        return repository.save(order);
    }

    @Transactional
    public SalesOrder cancel(String companyId, String orderId) {
        SalesOrder order = findOrder(companyId, orderId);
        if (order.getStatus() == SalesOrderStatus.DELIVERED) {
            throw new SalesOrderValidationException("No es pot cancel·lar una comanda ja lliurada");
        }
        order.setStatus(SalesOrderStatus.CANCELLED);
        return repository.save(order);
    }

    private SalesOrder findOrder(String companyId, String orderId) {
        SalesOrder order = repository.findById(orderId)
            .orElseThrow(() -> new SalesOrderNotFoundException(companyId, orderId));
        if (!Objects.equals(order.getCompany().getId(), companyId)) {
            throw new SalesOrderNotFoundException(companyId, orderId);
        }
        return order;
    }

    private Company findCompany(String companyId) {
        return companyRepository.findById(companyId).orElseThrow(() -> new CompanyNotFoundException(companyId));
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
            throw new SalesOrderValidationException("El partner de la comanda ha de ser un client");
        }
        if (!partner.isActive()) {
            throw new SalesOrderValidationException("No es pot fer una comanda per a un client inactiu");
        }
        return partner;
    }

    private List<SalesOrderLine> buildLines(SalesOrder order, List<SalesOrderLineCommand> commands) {
        List<SalesOrderLine> lines = new ArrayList<>();
        int index = 1;
        for (SalesOrderLineCommand command : commands) {
            validateLine(command);
            SalesOrderLine line = new SalesOrderLine();
            line.setSalesOrder(order);
            line.setLineOrder(index++);
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

    private List<SalesOrderLine> copyLines(SalesOrder order, Quote quote) {
        List<SalesOrderLine> lines = new ArrayList<>();
        int index = 1;
        for (var source : quote.getLines()) {
            SalesOrderLine line = new SalesOrderLine();
            line.setSalesOrder(order);
            line.setLineOrder(index++);
            line.setProductCode(source.getProductCode());
            line.setDescription(source.getDescription());
            line.setQuantity(source.getQuantity());
            line.setUnitPrice(source.getUnitPrice());
            line.setDiscountPercent(source.getDiscountPercent());
            line.setTaxRate(source.getTaxRate());
            lines.add(line);
        }
        return lines;
    }

    private void validateCommand(SalesOrderCommand command) {
        if (command.partnerId() == null || command.partnerId().isBlank()) {
            throw new SalesOrderValidationException("El client es obligatori");
        }
        if (command.orderDate() == null) {
            throw new SalesOrderValidationException("La data de la comanda es obligatoria");
        }
        if (command.deliveryDate() != null && command.deliveryDate().isBefore(command.orderDate())) {
            throw new SalesOrderValidationException("La data de lliurament no pot ser anterior a la data de la comanda");
        }
        if (command.lines() == null || command.lines().isEmpty()) {
            throw new SalesOrderValidationException("La comanda ha de tenir almenys una linia");
        }
    }

    private void validateLine(SalesOrderLineCommand command) {
        if (command.productCode() == null || command.productCode().isBlank()) {
            throw new SalesOrderValidationException("Cada linia ha de tenir un codi de producte");
        }
        if (command.description() == null || command.description().isBlank()) {
            throw new SalesOrderValidationException("Cada linia ha de tenir descripcio");
        }
        if (command.quantity() == null || command.quantity().compareTo(BigDecimal.ZERO) <= 0) {
            throw new SalesOrderValidationException("La quantitat de la linia ha de ser superior a 0");
        }
        if (command.unitPrice() == null || command.unitPrice().compareTo(BigDecimal.ZERO) < 0) {
            throw new SalesOrderValidationException("El preu unitari no pot ser negatiu");
        }
    }

    private SalesOrderStatus normalizeStatus(String status, boolean required) {
        if (status == null || status.isBlank()) {
            if (required) {
                throw new SalesOrderValidationException("L'estat de la comanda es obligatori");
            }
            return null;
        }
        try {
            return SalesOrderStatus.valueOf(status.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException exception) {
            throw new SalesOrderValidationException("L'estat de la comanda no es valid");
        }
    }

    private String normalizeSeries(String series) {
        return series == null || series.isBlank() ? "A" : series.trim().toUpperCase(Locale.ROOT);
    }

    private BigDecimal defaultZero(BigDecimal value) { return value == null ? BigDecimal.ZERO : value; }
    private BigDecimal defaultTax(BigDecimal value) { return value == null ? new BigDecimal("21.00") : value; }
    private BigDecimal scale(BigDecimal value, int scale) { return value.setScale(scale, RoundingMode.HALF_UP); }
    private String normalizeNullable(String value) { return value == null || value.isBlank() ? null : value.trim(); }
    private LocalDate effectiveDate(LocalDate value) { return value == null ? LocalDate.now() : value; }
}
