package cat.contacat.erp.common.api;

import cat.contacat.erp.core.company.CompanyAlreadyExistsException;
import cat.contacat.erp.core.company.CompanyNotFoundException;
import cat.contacat.erp.core.account.AccountAlreadyExistsException;
import cat.contacat.erp.core.account.AccountNotFoundException;
import cat.contacat.erp.core.account.AccountValidationException;
import cat.contacat.erp.core.journal.JournalEntryAlreadyPostedException;
import cat.contacat.erp.core.journal.JournalEntryNotFoundException;
import cat.contacat.erp.core.journal.JournalEntryValidationException;
import cat.contacat.erp.core.licensing.ModuleLicenseValidationException;
import cat.contacat.erp.core.partner.PartnerAlreadyExistsException;
import cat.contacat.erp.core.partner.PartnerNotFoundException;
import cat.contacat.erp.core.partner.PartnerValidationException;
import cat.contacat.erp.core.product.ProductAlreadyExistsException;
import cat.contacat.erp.core.product.ProductNotFoundException;
import cat.contacat.erp.core.sequence.DocumentSequenceNotFoundException;
import cat.contacat.erp.core.tax.TaxRateAlreadyExistsException;
import cat.contacat.erp.core.tax.TaxRateNotFoundException;
import cat.contacat.erp.core.warehouse.WarehouseAlreadyExistsException;
import cat.contacat.erp.core.warehouse.WarehouseNotFoundException;
import cat.contacat.erp.sales.quote.QuoteNotFoundException;
import cat.contacat.erp.sales.quote.QuoteValidationException;
import cat.contacat.erp.sales.order.SalesOrderNotFoundException;
import cat.contacat.erp.sales.order.SalesOrderValidationException;
import cat.contacat.erp.sales.invoice.SalesInvoiceNotFoundException;
import cat.contacat.erp.sales.invoice.SalesInvoiceValidationException;
import java.util.Map;
import java.util.stream.Collectors;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler({
        CompanyNotFoundException.class,
        AccountNotFoundException.class,
        JournalEntryNotFoundException.class,
        PartnerNotFoundException.class,
        ProductNotFoundException.class,
        WarehouseNotFoundException.class,
        TaxRateNotFoundException.class,
        DocumentSequenceNotFoundException.class,
        QuoteNotFoundException.class,
        SalesOrderNotFoundException.class,
        SalesInvoiceNotFoundException.class
    })
    public ResponseEntity<Map<String, String>> handleNotFound(RuntimeException exception) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", exception.getMessage()));
    }

    @ExceptionHandler({
        CompanyAlreadyExistsException.class,
        AccountAlreadyExistsException.class,
        JournalEntryAlreadyPostedException.class,
        PartnerAlreadyExistsException.class,
        ProductAlreadyExistsException.class,
        WarehouseAlreadyExistsException.class,
        TaxRateAlreadyExistsException.class
    })
    public ResponseEntity<Map<String, String>> handleConflict(RuntimeException exception) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("error", exception.getMessage()));
    }

    @ExceptionHandler(PartnerValidationException.class)
    public ResponseEntity<Map<String, String>> handlePartnerValidation(PartnerValidationException exception) {
        return ResponseEntity.badRequest().body(Map.of("error", exception.getMessage()));
    }

    @ExceptionHandler({
        AccountValidationException.class,
        JournalEntryValidationException.class,
        ModuleLicenseValidationException.class,
        QuoteValidationException.class,
        SalesOrderValidationException.class,
        SalesInvoiceValidationException.class
    })
    public ResponseEntity<Map<String, String>> handleBusinessValidation(RuntimeException exception) {
        return ResponseEntity.badRequest().body(Map.of("error", exception.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(MethodArgumentNotValidException exception) {
        Map<String, String> fields = exception.getBindingResult().getFieldErrors().stream()
            .collect(Collectors.toMap(
                FieldError::getField,
                error -> error.getDefaultMessage() == null ? "Valor invalid" : error.getDefaultMessage(),
                (first, second) -> first
            ));

        return ResponseEntity.badRequest().body(Map.of(
            "error", "Validacio fallida",
            "fields", fields
        ));
    }
}
