package cat.contacat.erp.sales.invoice;

import cat.contacat.erp.common.BaseEntity;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.journal.JournalEntry;
import cat.contacat.erp.core.partner.Partner;
import cat.contacat.erp.sales.order.SalesOrder;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.Index;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OrderBy;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

@Entity
@Table(
    name = "sales_invoices",
    uniqueConstraints = {
        @UniqueConstraint(name = "uq_sales_invoices_order", columnNames = "sales_order_id"),
        @UniqueConstraint(name = "uq_sales_invoices_company_number", columnNames = {"company_id", "invoice_number"}),
        @UniqueConstraint(name = "uq_sales_invoices_company_sequence", columnNames = {"company_id", "series", "fiscal_year", "sequence_number"})
    },
    indexes = {
        @Index(name = "ix_sales_invoices_company_date", columnList = "company_id, invoice_date"),
        @Index(name = "ix_sales_invoices_company_status", columnList = "company_id, status"),
        @Index(name = "ix_sales_invoices_partner", columnList = "partner_id")
    }
)
public class SalesInvoice extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "partner_id", nullable = false)
    private Partner partner;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "sales_order_id", nullable = false)
    private SalesOrder salesOrder;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "journal_entry_id", unique = true)
    private JournalEntry journalEntry;

    @Column(length = 20)
    private String series;

    @Column(name = "fiscal_year")
    private Integer fiscalYear;

    @Column(name = "sequence_number")
    private Integer sequenceNumber;

    @Column(name = "invoice_number", length = 50)
    private String invoiceNumber;

    @Column(name = "invoice_date", nullable = false)
    private LocalDate invoiceDate;

    @Column(name = "due_date", nullable = false)
    private LocalDate dueDate;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private SalesInvoiceStatus status = SalesInvoiceStatus.DRAFT;

    @Column(columnDefinition = "TEXT")
    private String notes;

    @Column(name = "issued_at")
    private OffsetDateTime issuedAt;

    @Column(name = "paid_at")
    private OffsetDateTime paidAt;

    @OneToMany(mappedBy = "salesInvoice", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("lineOrder ASC")
    private List<SalesInvoiceLine> lines = new ArrayList<>();

    @CreationTimestamp
    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private OffsetDateTime updatedAt;

    public Company getCompany() { return company; }
    public void setCompany(Company company) { this.company = company; }
    public Partner getPartner() { return partner; }
    public void setPartner(Partner partner) { this.partner = partner; }
    public SalesOrder getSalesOrder() { return salesOrder; }
    public void setSalesOrder(SalesOrder salesOrder) { this.salesOrder = salesOrder; }
    public JournalEntry getJournalEntry() { return journalEntry; }
    public void setJournalEntry(JournalEntry journalEntry) { this.journalEntry = journalEntry; }
    public String getSeries() { return series; }
    public void setSeries(String series) { this.series = series; }
    public Integer getFiscalYear() { return fiscalYear; }
    public void setFiscalYear(Integer fiscalYear) { this.fiscalYear = fiscalYear; }
    public Integer getSequenceNumber() { return sequenceNumber; }
    public void setSequenceNumber(Integer sequenceNumber) { this.sequenceNumber = sequenceNumber; }
    public String getInvoiceNumber() { return invoiceNumber; }
    public void setInvoiceNumber(String invoiceNumber) { this.invoiceNumber = invoiceNumber; }
    public LocalDate getInvoiceDate() { return invoiceDate; }
    public void setInvoiceDate(LocalDate invoiceDate) { this.invoiceDate = invoiceDate; }
    public LocalDate getDueDate() { return dueDate; }
    public void setDueDate(LocalDate dueDate) { this.dueDate = dueDate; }
    public SalesInvoiceStatus getStatus() { return status; }
    public void setStatus(SalesInvoiceStatus status) { this.status = status; }
    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
    public OffsetDateTime getIssuedAt() { return issuedAt; }
    public void setIssuedAt(OffsetDateTime issuedAt) { this.issuedAt = issuedAt; }
    public OffsetDateTime getPaidAt() { return paidAt; }
    public void setPaidAt(OffsetDateTime paidAt) { this.paidAt = paidAt; }
    public List<SalesInvoiceLine> getLines() { return lines; }
    public void setLines(List<SalesInvoiceLine> lines) { this.lines = lines; }
    public OffsetDateTime getCreatedAt() { return createdAt; }
    public OffsetDateTime getUpdatedAt() { return updatedAt; }
}
