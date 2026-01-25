import os

class Config:
    SAISON = 2026
    # GMX SMTP-Einstellungen
    MAIL_SERVER = "mail.gmx.net"
    MAIL_PORT = 587  # Port für TLS
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = MAIL_USERNAME