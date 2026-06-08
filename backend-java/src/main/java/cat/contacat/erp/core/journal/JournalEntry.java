package cat.contacat.erp.core.journal;

import cat.contacat.erp.common.BaseEntity;
import cat.contacat.erp.core.company.Company;
import cat.contacat.erp.core.sequence.DocumentSequence;
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
    name = "journal_entries",
    uniqueConstraints = @UniqueConstraint(name = "uq_journal_entries_company_number", columnNames = {"company_id", "entry_number"}),
    indexes = {
        @Index(name = "ix_journal_entries_company_date", columnList = "company_id, entry_date"),
        @Index(name = "ix_journal_entries_company_status", columnList = "company_id, status")
    }
)
public class JournalEntry extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "sequence_id", nullable = false)
    private DocumentSequence sequence;

    @Column(name = "entry_number", nullable = false)
    private int entryNumber;

    @Column(name = "formatted_number", nullable = false, length = 50)
    private String formattedNumber;

    @Column(name = "entry_date", nullable = false)
    private LocalDate entryDate;

    @Column(nullable = false, length = 500)
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private JournalEntryStatus status = JournalEntryStatus.DRAFT;

    @Column(name = "attachment_path", length = 255)
    private String attachmentPath;

    @CreationTimestamp
    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private OffsetDateTime updatedAt;

    @Column(name = "posted_at")
    private OffsetDateTime postedAt;

    @OneToMany(mappedBy = "journalEntry", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("lineOrder ASC")
    private List<JournalLine> lines = new ArrayList<>();

    public Company getCompany() { return company; }
    public void setCompany(Company company) { this.company = company; }
    public DocumentSequence getSequence() { return sequence; }
    public void setSequence(DocumentSequence sequence) { this.sequence = sequence; }
    public int getEntryNumber() { return entryNumber; }
    public void setEntryNumber(int entryNumber) { this.entryNumber = entryNumber; }
    public String getFormattedNumber() { return formattedNumber; }
    public void setFormattedNumber(String formattedNumber) { this.formattedNumber = formattedNumber; }
    public LocalDate getEntryDate() { return entryDate; }
    public void setEntryDate(LocalDate entryDate) { this.entryDate = entryDate; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public JournalEntryStatus getStatus() { return status; }
    public void setStatus(JournalEntryStatus status) { this.status = status; }
    public String getAttachmentPath() { return attachmentPath; }
    public void setAttachmentPath(String attachmentPath) { this.attachmentPath = attachmentPath; }
    public OffsetDateTime getCreatedAt() { return createdAt; }
    public OffsetDateTime getUpdatedAt() { return updatedAt; }
    public OffsetDateTime getPostedAt() { return postedAt; }
    public void setPostedAt(OffsetDateTime postedAt) { this.postedAt = postedAt; }
    public List<JournalLine> getLines() { return lines; }
    public void setLines(List<JournalLine> lines) { this.lines = lines; }
}
