"""Email service for sending emails via SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        """Initialize email service with configuration."""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT',  '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('SMTP_FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('SMTP_FROM_NAME', 'ContaCAT ERP')
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (fallback)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_password_reset_email(self, to_email: str, reset_link: str, username: str) -> bool:
        """
        Send password reset email.
        
        Args:
            to_email: User's email address
            reset_link: Password reset link with token
            username: User's username
        
        Returns:
            True if email sent successfully
        """
        subject = "Restabliment de Contrasenya - ContaCAT ERP"
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; color: white; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .button:hover {{ background: #5568d3; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Restabliment de Contrasenya</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{username}</strong>,</p>
                    <p>Hem rebut una sol·licitud per restablir la contrasenya del teu compte a ContaCAT ERP.</p>
                    <p>Fes clic al botó següent per crear una nova contrasenya:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Restablir Contrasenya</a>
                    </p>
                    <div class="warning">
                        <strong>⏱️ Important:</strong> Aquest enllaç només és vàlid durant <strong>30 minuts</strong>.
                    </div>
                    <p>Si no has sol·licitat aquest canvi, ignora aquest correu i la teva contrasenya es mantindrà sense canvis.</p>
                    <p>Per motius de seguretat, no comparteixis aquest enllaç amb ningú.</p>
                </div>
                <div class="footer">
                    <p>Aquest és un correu automàtic. Si us plau, no responguis a aquest missatge.</p>
                    <p>&copy; 2024 ContaCAT ERP. Tots els drets reservats.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_content = f"""
        Hola {username},
        
        Hem rebut una sol·licitud per restablir la contrasenya del teu compte a ContaCAT ERP.
        
        Fes clic a l'enllaç següent per crear una nova contrasenya:
        {reset_link}
        
        IMPORTANT: Aquest enllaç només és vàlid durant 30 minuts.
        
        Si no has sol·licitat aquest canvi, ignora aquest correu i la teva contrasenya es mantindrà sense canvis.
        
        --
        ContaCAT ERP
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
