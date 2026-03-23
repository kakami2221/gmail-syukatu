from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from app.routes import sync_gmail_to_db


app = create_app()


with app.app_context():
    sync_gmail_to_db()
    print("Gmail sync completed.")
