from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'instance' / 'jobmail.db').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GMAIL_CREDENTIALS_PATH = os.getenv(
        "GMAIL_CREDENTIALS_PATH",
        str(BASE_DIR / "credentials" / "credentials.json"),
    )
    GMAIL_TOKEN_PATH = os.getenv(
        "GMAIL_TOKEN_PATH",
        str(BASE_DIR / "credentials" / "token.json"),
    )
    GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    JOBMAIL_LABEL_PREFIX = os.getenv("JOBMAIL_LABEL_PREFIX", "就活")
    GMAIL_QUERY = os.getenv(
        "GMAIL_QUERY",
        "(採用 OR 就活 OR 面接 OR 説明会 OR エントリー OR ES OR SPI OR 適性検査)",
    )
    MAIL_FETCH_MAX_RESULTS = int(os.getenv("MAIL_FETCH_MAX_RESULTS", "50"))
