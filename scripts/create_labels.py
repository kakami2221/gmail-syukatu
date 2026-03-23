from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.gmail_service import GmailService


app = create_app()


with app.app_context():
    service = GmailService(app)
    labels = service.ensure_jobmail_labels()
    print(f"Prepared {len(labels)} labels.")
