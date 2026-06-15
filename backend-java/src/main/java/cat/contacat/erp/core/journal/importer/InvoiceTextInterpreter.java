package cat.contacat.erp.core.journal.importer;

import cat.contacat.erp.core.journal.JournalEntryValidationException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.springframework.stereotype.Component;

@Component
public class InvoiceTextInterpreter {

    private static final Pattern DATE = Pattern.compile("\\b(\\d{1,2}[/-]\\d{1,2}[/-]\\d{4})\\b");
    private static final Pattern INVOICE_NUMBER = Pattern.compile(
        "(?i)(?:factura|invoice)(?:\\s+n(?:um(?:ero)?|úm(?:ero)?)?\\.?|\\s*#)?\\s*[:\\-]?\\s*([A-Z0-9][A-Z0-9/\\-_.]+)"
    );
    private static final Pattern TOTAL = amountPattern("(?:total\\s+factura|total\\s+a\\s+pagar|import\\s+total|total)");
    private static final Pattern TAX = amountPattern("(?:quota\\s+iva|cuota\\s+iva|iva)");
    private static final Pattern BASE = amountPattern("(?:base\\s+imposable|base\\s+imponible|subtotal)");

    public InvoiceDocumentData interpret(String text) {
        String normalized = text == null ? "" : text.replace('\u00a0', ' ');
        BigDecimal total = findAmount(TOTAL, normalized);
        if (total == null || total.compareTo(BigDecimal.ZERO) <= 0) {
            throw new JournalEntryValidationException("No s'ha pogut identificar un total valid a la factura PDF");
        }

        BigDecimal tax = defaultZero(findAmount(TAX, normalized));
        BigDecimal base = findAmount(BASE, normalized);
        List<String> warnings = new ArrayList<>();
        if (base == null) {
            base = total.subtract(tax).setScale(2, RoundingMode.HALF_UP);
            warnings.add("Base imposable calculada a partir del total i l'IVA");
        }
        if (base.add(tax).compareTo(total) != 0) {
            warnings.add("Els imports detectats no quadren; cal revisar la proposta");
        }

        LocalDate date = findDate(normalized);
        if (date == null) {
            date = LocalDate.now();
            warnings.add("Data no detectada; s'ha utilitzat la data actual");
        }
        String number = findGroup(INVOICE_NUMBER, normalized);
        if (number == null) warnings.add("Numero de factura no detectat");

        int confidence = Math.max(25, 100 - warnings.size() * 20);
        return new InvoiceDocumentData(date, null, number, base, tax, total, confidence, List.copyOf(warnings));
    }

    private static Pattern amountPattern(String label) {
        return Pattern.compile("(?i)" + label + "\\s*[:\\-]?\\s*(?:EUR|€)?\\s*([0-9][0-9.,]*)\\s*(?:EUR|€)?");
    }

    private BigDecimal findAmount(Pattern pattern, String text) {
        String value = findGroup(pattern, text);
        if (value == null) return null;
        String normalized = value.lastIndexOf(',') > value.lastIndexOf('.')
            ? value.replace(".", "").replace(',', '.')
            : value.replace(",", "");
        try {
            return new BigDecimal(normalized).setScale(2, RoundingMode.HALF_UP);
        } catch (NumberFormatException exception) {
            return null;
        }
    }

    private LocalDate findDate(String text) {
        String value = findGroup(DATE, text);
        if (value == null) return null;
        String normalized = value.replace('-', '/');
        try {
            return LocalDate.parse(normalized, DateTimeFormatter.ofPattern("d/M/uuuu", Locale.ROOT));
        } catch (RuntimeException exception) {
            return null;
        }
    }

    private String findGroup(Pattern pattern, String text) {
        Matcher matcher = pattern.matcher(text);
        return matcher.find() ? matcher.group(1).trim() : null;
    }

    private BigDecimal defaultZero(BigDecimal value) {
        return value == null ? BigDecimal.ZERO.setScale(2) : value;
    }
}
