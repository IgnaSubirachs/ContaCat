package cat.contacat.erp.core.journal.importer;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.ByteArrayOutputStream;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts.FontName;
import org.junit.jupiter.api.Test;

class PdfInvoiceDocumentReaderTest {

    @Test
    void readsInvoiceDataFromRealPdfBytes() throws Exception {
        InvoiceDocumentData result = new PdfInvoiceDocumentReader(new InvoiceTextInterpreter()).read(invoicePdf());

        assertThat(result.invoiceNumber()).isEqualTo("F-2026-19");
        assertThat(result.taxableBase()).isEqualByComparingTo("100.00");
        assertThat(result.taxAmount()).isEqualByComparingTo("21.00");
        assertThat(result.total()).isEqualByComparingTo("121.00");
    }

    private byte[] invoicePdf() throws Exception {
        try (PDDocument document = new PDDocument(); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            PDPage page = new PDPage();
            document.addPage(page);
            try (PDPageContentStream content = new PDPageContentStream(document, page)) {
                content.beginText();
                content.setFont(new PDType1Font(FontName.HELVETICA), 12);
                content.newLineAtOffset(50, 750);
                content.showText("Factura F-2026-19");
                content.newLineAtOffset(0, -20);
                content.showText("Data: 15/06/2026");
                content.newLineAtOffset(0, -20);
                content.showText("Base imposable: 100,00 EUR");
                content.newLineAtOffset(0, -20);
                content.showText("Quota IVA: 21,00 EUR");
                content.newLineAtOffset(0, -20);
                content.showText("Total factura: 121,00 EUR");
                content.endText();
            }
            document.save(output);
            return output.toByteArray();
        }
    }
}
