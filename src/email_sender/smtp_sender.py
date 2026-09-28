import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any, Dict

from src.config import Config


class SmtpSender:
    def __init__(self, smtp_config: Dict[str, Any]):
        self.host = Config.SMTP_HOST or smtp_config.get('host', '')
        self.port = Config.SMTP_PORT or int(smtp_config.get('port', 0) or 0)
        self.username = Config.SMTP_USERNAME or smtp_config.get('username', '')
        self.password = Config.SMTP_PASSWORD or smtp_config.get('password', '')
        self.from_address = (
            Config.SMTP_FROM_ADDRESS
            or smtp_config.get('from_address', '')
        )
        self.from_name = (
            Config.SMTP_FROM_NAME
            or smtp_config.get('from_name', 'Company Parser')
        )
        self.use_ssl = Config.SMTP_USE_SSL

    def send(self, to_address: str, subject: str, body: str) -> None:
        if not self.host or not self.port:
            raise RuntimeError("SMTP host/port not configured")
        if not self.from_address:
            raise RuntimeError("SMTP from_address not configured")

        message = MIMEText(body, 'plain', 'utf-8')
        message['Subject'] = subject
        message['From'] = formataddr((self.from_name, self.from_address))
        message['To'] = to_address

        if self.use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.host, self.port, context=context, timeout=30) as server:
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(message)
        else:
            with smtplib.SMTP(self.host, self.port, timeout=30) as server:
                server.starttls(context=ssl.create_default_context())
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(message)
