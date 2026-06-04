package cat.contacat.erp.core.sequence;

public record DocumentNumber(
    String sequenceId,
    String companyId,
    String documentType,
    String series,
    int fiscalYear,
    int number,
    String formattedNumber
) {
}
