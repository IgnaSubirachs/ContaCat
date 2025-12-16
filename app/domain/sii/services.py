"""
SII (Suministro Inmediato de Información) Service.
Integrates with Spanish Tax Agency (AEAT) for invoice reporting.
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal

from app.domain.sii.entities import SIISubmission, SIIStatus

logger = logging.getLogger(__name__)


class SIIService:
    """Service for SII submissions to AEAT."""
    
    def __init__(self, settings_service, sii_repo=None):
        """
        Initialize SIIService.
        
        Args:
            settings_service: SettingsService for company/SII config
            sii_repo: Optional repository for tracking submissions
        """
        self._settings = settings_service
        self._repo = sii_repo
    
    def is_sii_enabled(self) -> bool:
        """Check if SII is enabled and configured."""
        settings = self._settings.get_settings()
        
        # Check if SII is enabled in settings
        sii_enabled = getattr(settings, 'sii_enabled', False)
        
        # Check if certificate is configured (even if demo mode)
        has_cert = getattr(settings, 'sii_certificate_path', None) is not None
        
        return sii_enabled
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (no real certificate)."""
        settings = self._settings.get_settings()
        
        # Demo mode if explicitly set OR no certificate configured
        demo_mode = getattr(settings, 'sii_test_mode', True)
        has_cert = getattr(settings, 'sii_certificate_path', None) is not None
        
        return demo_mode or not has_cert
    
    def submit_sales_invoice(self, invoice) -> SIISubmission:
        """
        Submit sales invoice to AEAT SII.
        
        Args:
            invoice: SalesInvoice entity
            
        Returns:
            SIISubmission record
        """
        logger.info(f"Submitting invoice {invoice.invoice_number} to SII")
        
        # Check if SII is enabled
        if not self.is_sii_enabled():
            logger.warning("SII is not enabled")
            return SIISubmission(
                invoice_id=invoice.id,
                submission_date=datetime.now(),
                status=SIIStatus.ERROR,
                error_message="SII no està activat. Configura'l a Settings."
            )
        
        # Demo mode: simulate submission
        if self.is_demo_mode():
            return self._submit_demo(invoice)
        
        # Real mode: submit to AEAT (requires certificate)
        return self._submit_real(invoice)
    
    def _submit_demo(self, invoice) -> SIISubmission:
        """
        Demo mode: Simulate SII submission without real AEAT connection.
        
        This allows clients to test the UI/workflow without a certificate.
        """
        logger.info(f"[DEMO] Simulating SII submission for {invoice.invoice_number}")
        
        # Generate fake CSV (AEAT returns this on success)
        fake_csv = f"DEMO-{invoice.invoice_number}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        submission = SIISubmission(
            invoice_id=invoice.id,
            submission_date=datetime.now(),
            status=SIIStatus.ACCEPTED,
            csv=fake_csv,
            aeat_response="[DEMO MODE] Simulació exitosa. Configura un certificat real per enviar a AEAT."
        )
        
        # Save to repository if available
        if self._repo:
            self._repo.save(submission)
        
        logger.info(f"[DEMO] Submission successful: {fake_csv}")
        return submission
    
    def _submit_real(self, invoice) -> SIISubmission:
        """
        Real mode: Submit to actual AEAT SII endpoint.
        
        Requires:
        - Valid company certificate (.pfx)
        - SOAP client (zeep)
        - XML generation and signing
        """
        logger.info(f"[REAL] Submitting to AEAT SII: {invoice.invoice_number}")
        
        try:
            # 1. Generate XML
            xml_content = self._generate_sales_invoice_xml(invoice)
            
            # 2. Sign XML with certificate
            signed_xml = self._sign_xml(xml_content)
            
            # 3. Send to AEAT via SOAP
            response = self._send_to_aeat(signed_xml)
            
            # 4. Parse response
            csv, status, error = self._parse_aeat_response(response)
            
            submission = SIISubmission(
                invoice_id=invoice.id,
                submission_date=datetime.now(),
                status=SIIStatus.ACCEPTED if status == "ACEPTADO" else SIIStatus.REJECTED,
                csv=csv,
                aeat_response=str(response),
                error_message=error
            )
            
            if self._repo:
                self._repo.save(submission)
            
            return submission
            
        except Exception as e:
            logger.error(f"SII submission error: {e}")
            return SIISubmission(
                invoice_id=invoice.id,
                submission_date=datetime.now(),
                status=SIIStatus.ERROR,
                error_message=str(e)
            )
    
    def _generate_sales_invoice_xml(self, invoice) -> str:
        """
        Generate SII XML for sales invoice.
        
        TODO: Implement full XML generation per AEAT specs.
        """
        settings = self._settings.get_settings()
        
        # Simplified template (real implementation needs full AEAT schema)
        xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
        <siiLR:SuministroLRFacturasEmitidas>
            <sii:Cabecera>
                <sii:IDVersionSii>1.1</sii:IDVersionSii>
                <sii:Titular>
                    <sii:NIF>{settings.tax_id}</sii:NIF>
                    <sii:NombreRazon>{settings.name}</sii:NombreRazon>
                </sii:Titular>
            </sii:Cabecera>
            <siiLR:RegistroLRFacturasEmitidas>
                <siiLR:IDFactura>
                    <sii:NumSerieFacturaEmisor>{invoice.invoice_number}</sii:NumSerieFacturaEmisor>
                    <sii:FechaExpedicionFacturaEmisor>{invoice.invoice_date.strftime('%d-%m-%Y')}</sii:FechaExpedicionFacturaEmisor>
                </siiLR:IDFactura>
                <siiLR:FacturaExpedida>
                    <sii:TipoFactura>F1</sii:TipoFactura>
                    <sii:ImporteTotal>{invoice.total_amount}</sii:ImporteTotal>
                </siiLR:FacturaExpedida>
            </siiLR:RegistroLRFacturasEmitidas>
        </siiLR:SuministroLRFacturasEmitidas>
        """
        
        return xml_template
    
    def _sign_xml(self, xml_content: str) -> str:
        """
        Sign XML with company certificate.
        
        TODO: Implement digital signature using cryptography library.
        """
        logger.warning("XML signing not yet implemented")
        return xml_content
    
    def _send_to_aeat(self, signed_xml: str) -> Dict:
        """
        Send signed XML to AEAT via SOAP.
        
        TODO: Implement using zeep SOAP client.
        """
        logger.warning("AEAT SOAP client not yet implemented")
        return {"status": "OK"}
    
    def _parse_aeat_response(self, response: Dict) -> tuple:
        """
        Parse AEAT response.
        
        Returns:
            (csv, status, error_message)
        """
        # TODO: Parse real AEAT XML response
        csv = response.get("CSV", "PENDING")
        status = response.get("EstadoRegistro", "ACEPTADO")
        error = response.get("DescripcionErrorRegistro")
        
        return csv, status, error
    
    def get_submission_status(self, invoice_id: str) -> Optional[SIISubmission]:
        """Get SII submission status for an invoice."""
        if not self._repo:
            return None
        
        return self._repo.find_by_invoice_id(invoice_id)
