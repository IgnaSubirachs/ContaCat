package cat.contacat.erp.core.sequence;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import cat.contacat.erp.core.company.Company;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class DocumentSequenceServiceTest {

    @Mock
    private DocumentSequenceRepository repository;

    @InjectMocks
    private DocumentSequenceService service;

    @Test
    void allocateNextLocksSequenceIncrementsAndReturnsFormattedNumber() {
        Company company = new Company();
        company.setId("company-1");

        DocumentSequence sequence = new DocumentSequence();
        sequence.setId("sequence-1");
        sequence.setCompany(company);
        sequence.setDocumentType("SALES_INVOICE");
        sequence.setSeries("A");
        sequence.setFiscalYear(2026);
        sequence.setPrefix("FV-2026-");
        sequence.setPadding(4);
        sequence.setNextNumber(42);

        when(repository.lockActiveSequence("company-1", "SALES_INVOICE", "A", 2026))
            .thenReturn(Optional.of(sequence));

        DocumentNumber number = service.allocateNext("company-1", "SALES_INVOICE", "a", 2026);

        assertThat(number.sequenceId()).isEqualTo("sequence-1");
        assertThat(number.number()).isEqualTo(42);
        assertThat(number.formattedNumber()).isEqualTo("FV-2026-0042");
        assertThat(sequence.getNextNumber()).isEqualTo(43);
        verify(repository).save(sequence);
    }

    @Test
    void allocateNextUsesDefaultSeriesAWhenSeriesIsBlank() {
        DocumentSequence sequence = new DocumentSequence();
        sequence.setId("sequence-2");
        sequence.setDocumentType("JOURNAL_ENTRY");
        sequence.setSeries("A");
        sequence.setFiscalYear(2026);
        sequence.setPrefix("JE-");
        sequence.setPadding(3);
        sequence.setNextNumber(7);

        when(repository.lockActiveSequence("company-1", "JOURNAL_ENTRY", "A", 2026))
            .thenReturn(Optional.of(sequence));

        DocumentNumber number = service.allocateNext("company-1", "JOURNAL_ENTRY", " ", 2026);

        assertThat(number.formattedNumber()).isEqualTo("JE-007");
    }

    @Test
    void allocateNextFailsWhenNoActiveSequenceExists() {
        when(repository.lockActiveSequence("company-1", "SALES_INVOICE", "A", 2026))
            .thenReturn(Optional.empty());

        assertThatThrownBy(() -> service.allocateNext("company-1", "SALES_INVOICE", "A", 2026))
            .isInstanceOf(DocumentSequenceNotFoundException.class);
    }
}
