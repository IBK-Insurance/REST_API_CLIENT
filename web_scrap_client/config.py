import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GOOGLE_PLAY_URL = os.getenv('GOOGLE_PLAY_URL')
    TARGET_APP_ID = os.getenv('TARGET_APP_ID')
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
    # Parse multiple emails separated by comma
    RECIPIENT_EMAILS = [email.strip() for email in os.getenv('RECIPIENT_EMAIL', '').split(',') if email.strip()]

    @staticmethod
    def validate():
        required_vars = [
            'TARGET_APP_ID', 'SMTP_SERVER', 'SENDER_EMAIL', 
            'SENDER_PASSWORD', 'RECIPIENT_EMAILS'
        ]
        missing = [var for var in required_vars if not getattr(Config, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
