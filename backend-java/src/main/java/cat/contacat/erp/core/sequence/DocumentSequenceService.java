package cat.contacat.erp.core.sequence;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
public class DocumentSequenceService {

    private final DocumentSequenceRepository repository;

    public DocumentSequenceService(DocumentSequenceRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public DocumentNumber allocateNext(String companyId, String documentType, String series, int fiscalYear) {
        String normalizedSeries = normalizeSeries(series);
        DocumentSequence sequence = repository
            .lockActiveSequence(companyId, documentType, normalizedSeries, fiscalYear)
            .orElseThrow(() -> new DocumentSequenceNotFoundException(companyId, documentType, normalizedSeries, fiscalYear));

        int allocatedNumber = sequence.getNextNumber();
        sequence.setNextNumber(allocatedNumber + 1);
        repository.save(sequence);

        return new DocumentNumber(
            sequence.getId(),
            companyId,
            sequence.getDocumentType(),
            sequence.getSeries(),
            sequence.getFiscalYear(),
            allocatedNumber,
            format(sequence, allocatedNumber)
        );
    }

    private String normalizeSeries(String series) {
        if (!StringUtils.hasText(series)) {
            return "A";
        }
        return series.trim().toUpperCase();
    }

    private String format(DocumentSequence sequence, int number) {
        String padded = String.format("%0" + sequence.getPadding() + "d", number);
        return sequence.getPrefix() + padded;
    }
}
