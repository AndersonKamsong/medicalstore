# medicalstore/custom_email_backend.py
import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend

class CustomSSLEmailBackend(SMTPBackend):
    def open(self):
        """
        Override the open method to handle SSL connections better
        """
        if self.connection:
            return False
        
        try:
            # Create SSL context with relaxed settings
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Connect using SMTP_SSL
            self.connection = smtplib.SMTP_SSL(
                self.host, 
                self.port, 
                context=ssl_context,
                timeout=self.timeout
            )
            
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            
            return True
            
        except Exception as e:
            if not self.fail_silently:
                raise
            return False