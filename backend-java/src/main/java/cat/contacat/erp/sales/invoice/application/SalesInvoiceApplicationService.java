package cat.contacat.erp.sales.invoice.application;

import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.company.CompanyRepository;
import cat.contacat.erp.core.sequence.DocumentNumber;
import cat.contacat.erp.core.sequence.DocumentSequenceService;
import cat.contacat.erp.sales.invoice.SalesInvoice;
import cat.contacat.erp.sales.invoice.SalesInvoiceLine;
import cat.contacat.erp.sales.invoice.SalesInvoiceNotFoundException;
import cat.contacat.erp.sales.invoice.SalesInvoiceRepository;
import cat.contacat.erp.sales.invoice.SalesInvoiceStatus;
import cat.contacat.erp.sales.invoice.SalesInvoiceValidationException;
import cat.contacat.erp.sales.order.SalesOrder;
import cat.contacat.erp.sales.order.SalesOrderNotFoundException;
import cat.contacat.erp.sales.order.SalesOrderRepository;
import cat.contacat.erp.sales.order.SalesOrderStatus;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class SalesInvoiceApplicationService {

    private final SalesInvoiceRepository repository;
    private final SalesOrderRepository orderRepository;
    private final CompanyRepository companyRepository;
    private final DocumentSequenceService documentSequenceService;

    public SalesInvoiceApplicationService(
        SalesInvoiceRepository repository,
        SalesOrderRepository orderRepository,
        CompanyRepository companyRepository,
        DocumentSequenceService documentSequenceService
    ) {
        this.repository = repository;
        this.orderRepository = orderRepository;
        this.companyRepository = companyRepository;
        this.documentSequenceService = documentSequenceService;
    }

    @Transactional(readOnly = true)
    public List<SalesInvoice> list(String companyId, String status) {
        ensureCompanyExists(companyId);
        SalesInvoiceStatus normalized = normalizeStatus(status);
        return normalized == null
            ? repository.findAllByCompanyIdOrderByInvoiceDateDescCreatedAtDesc(companyId)
            : repository.findAllByCompanyIdAndStatusOrderByInvoiceDateDescCreatedAtDesc(companyId, normalized);
    }

    @Transactional(readOnly = true)
    public SalesInvoice get(String companyId, String invoiceId) {
        return findInvoice(companyId, invoiceId);
    }

    @Transactional
    public SalesInvoice createFromOrder(String companyId, String orderId, LocalDate invoiceDate, LocalDate dueDate) {
        SalesOrder order = findOrder(companyId, orderId);
        if (order.getStatus() != SalesOrderStatus.DELIVERED) {
            throw new SalesInvoiceValidationException("Nomes es poden facturar comandes lliurades");
        }
        if (repository.existsBySalesOrderId(orderId)) {
            throw new SalesInvoiceValidationException("La comanda ja te una factura associada");
        }

        LocalDate effectiveInvoiceDate = invoiceDate == null ? LocalDate.now() : invoiceDate;
        LocalDate effectiveDueDate = dueDate == null ? effectiveInvoiceDate.plusDays(30) : dueDate;
        if (effectiveDueDate.isBefore(effectiveInvoiceDate)) {
            throw new SalesInvoiceValidationException("La data de venciment no pot ser anterior a la data de factura");
        }

        SalesInvoice invoice = new SalesInvoice();
        invoice.setCompany(order.getCompany());
        invoice.setPartner(order.getPartner());
        invoice.setSalesOrder(order);
        invoice.setInvoiceDate(effectiveInvoiceDate);
        invoice.setDueDate(effectiveDueDate);
        invoice.setNotes(order.getNotes());
        invoice.setStatus(SalesInvoiceStatus.DRAFT);
        invoice.setLines(copyLines(invoice, order));
        return repository.save(invoice);
    }

    @Transactional
    public SalesInvoice issue(String companyId, String invoiceId) {
        SalesInvoice invoice = findInvoice(companyId, invoiceId);
        if (invoice.getStatus() != SalesInvoiceStatus.DRAFT) {
            throw new SalesInvoiceValidationException("Nomes es poden emetre factures en esborrany");
        }
        DocumentNumber allocated = documentSequenceService.allocateNext(
            companyId,
            "SALES_INVOICE",
            "A",
            invoice.getInvoiceDate().getYear()
        );
        invoice.setSeries(allocated.series());
        invoice.setFiscalYear(allocated.fiscalYear());
        invoice.setSequenceNumber(allocated.number());
        invoice.setInvoiceNumber(allocated.formattedNumber());
        invoice.setStatus(SalesInvoiceStatus.ISSUED);
        invoice.setIssuedAt(OffsetDateTime.now());
        return repository.save(invoice);
    }

    @Transactional
    public SalesInvoice markPaid(String companyId, String invoiceId) {
        SalesInvoice invoice = findInvoice(companyId, invoiceId);
        if (invoice.getStatus() != SalesInvoiceStatus.ISSUED) {
            throw new SalesInvoiceValidationException("Nomes es poden cobrar factures emeses");
        }
        invoice.setStatus(SalesInvoiceStatus.PAID);
        invoice.setPaidAt(OffsetDateTime.now());
        return repository.save(invoice);
    }

    @Transactional
    public void deleteDraft(String companyId, String invoiceId) {
        SalesInvoice invoice = findInvoice(companyId, invoiceId);
        if (invoice.getStatus() != SalesInvoiceStatus.DRAFT) {
            throw new SalesInvoiceValidationException("Una factura emesa no es pot eliminar; cal generar una rectificativa");
        }
        repository.delete(invoice);
    }

    private SalesInvoice findInvoice(String companyId, String invoiceId) {
        SalesInvoice invoice = repository.findById(invoiceId)
            .orElseThrow(() -> new SalesInvoiceNotFoundException(companyId, invoiceId));
        if (!Objects.equals(invoice.getCompany().getId(), companyId)) {
            throw new SalesInvoiceNotFoundException(companyId, invoiceId);
        }
        return invoice;
    }

    private SalesOrder findOrder(String companyId, String orderId) {
        SalesOrder order = orderRepository.findById(orderId)
            .orElseThrow(() -> new SalesOrderNotFoundException(companyId, orderId));
        if (!Objects.equals(order.getCompany().getId(), companyId)) {
            throw new SalesOrderNotFoundException(companyId, orderId);
        }
        return order;
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new CompanyNotFoundException(companyId);
        }
    }

    private List<SalesInvoiceLine> copyLines(SalesInvoice invoice, SalesOrder order) {
        List<SalesInvoiceLine> lines = new ArrayList<>();
        int index = 1;
        for (var source : order.getLines()) {
            SalesInvoiceLine line = new SalesInvoiceLine();
            line.setSalesInvoice(invoice);
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

    private SalesInvoiceStatus normalizeStatus(String status) {
        if (status == null || status.isBlank()) {
            return null;
        }
        try {
            return SalesInvoiceStatus.valueOf(status.trim().toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException exception) {
            throw new SalesInvoiceValidationException("L'estat de la factura no es valid");
        }
    }
}
