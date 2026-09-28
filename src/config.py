import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    PARSER_API_URL: str = os.getenv('PARSER_API_URL', 'http://127.0.0.1:5050').rstrip('/')
    PARSER_API_KEY: str = os.getenv('PARSER_API_KEY', '').strip()

    SUBSCRIBERS_FILE: Path = Path(os.getenv('SUBSCRIBERS_FILE', '/data/subscribers.json'))
    SUBSCRIBERS_DEFAULT: Path = Path('/app/data/subscribers.default.json')

    SMTP_HOST: str = os.getenv('SMTP_HOST', '').strip()
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '0') or 0)
    SMTP_USERNAME: str = os.getenv('SMTP_USERNAME', '').strip()
    SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD', '').strip()
    SMTP_FROM_ADDRESS: str = os.getenv('SMTP_FROM_ADDRESS', '').strip()
    SMTP_FROM_NAME: str = os.getenv('SMTP_FROM_NAME', 'Company Parser').strip()
    SMTP_USE_SSL: bool = os.getenv('SMTP_USE_SSL', 'true').lower() == 'true'

    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/email.log')


Path('logs').mkdir(exist_ok=True)
