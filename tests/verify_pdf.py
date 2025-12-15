import sys
import os
import io

# Ensure app modules are importable
sys.path.insert(0, os.getcwd())

from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.sales.repository import SqlAlchemySalesInvoiceRepository
from app.infrastructure.persistence.partners.repository import SqlAlchemyPartnerRepository
from app.domain.sales.pdf_service import PdfService
from app.interface.api.templates import templates

def verify_pdf_generation():
    print("[INFO] Starting PDF Verification...")
    
    session = SessionLocal()
    try:
        # Get an invoice
        invoice_repo = SqlAlchemySalesInvoiceRepository( lambda: session )
        partner_repo = SqlAlchemyPartnerRepository( lambda: session )
        
        invoices = invoice_repo.list_all()
        if not invoices:
            print("[WARN] No invoices found to test PDF generation.")
            return
            
        invoice = invoices[0]
        print(f"[INFO] Testing with Invoice: {invoice.invoice_number} ({invoice.id})")
        
        partner = partner_repo.find_by_id(invoice.partner_id)
        
        # Instantiate Service
        pdf_service = PdfService(templates)
        
        # Generate PDF
        print("[INFO] Generating PDF bytes...")
        try:
            pdf_bytes = pdf_service.generate_invoice_pdf(invoice, partner)
        except Exception as e:
            print(f"[ERROR] PDF Generation failed: {e}")
            raise e
            
        print(f"[SUCCESS] PDF generated! Size: {len(pdf_bytes)} bytes")
        
        # Save sample
        output_file = f"test_invoice_{invoice.invite_number if hasattr(invoice, 'invoice_number') else 'sample'}.pdf"
        with open(output_file, "wb") as f:
            f.write(pdf_bytes)
        print(f"[INFO] Saved sample to {output_file}")
            
    except Exception as e:
        print(f"[ERROR] Logic failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_pdf_generation()
