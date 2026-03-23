from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .classifier import LABELS
from .utils import extract_plain_text, extract_sender_parts, parse_gmail_datetime


class GmailService:
    def __init__(self, app):
        self.app = app
        self._service = None

    def get_client(self):
        if self._service:
            return self._service

        creds = None
        token_path = Path(self.app.config["GMAIL_TOKEN_PATH"])
        credentials_path = Path(self.app.config["GMAIL_CREDENTIALS_PATH"])
        scopes = self.app.config["GMAIL_SCOPES"]

        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), scopes
                )
                creds = flow.run_local_server(port=0)

            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(creds.to_json(), encoding="utf-8")

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def list_messages(self, query=None, max_results=None):
        service = self.get_client()
        params = {"userId": "me", "q": query or self.app.config["GMAIL_QUERY"]}
        if max_results:
            params["maxResults"] = max_results
        response = service.users().messages().list(**params).execute()
        return response.get("messages", [])

    def get_message(self, message_id):
        service = self.get_client()
        payload = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        headers = {
            item["name"]: item["value"]
            for item in payload.get("payload", {}).get("headers", [])
        }
        sender_name, sender_email = extract_sender_parts(headers.get("From", ""))

        return {
            "gmail_message_id": payload["id"],
            "gmail_thread_id": payload["threadId"],
            "subject": headers.get("Subject", ""),
            "sender": headers.get("From", ""),
            "sender_name": sender_name,
            "sender_email": sender_email,
            "received_at": parse_gmail_datetime(payload.get("internalDate")),
            "snippet": payload.get("snippet", ""),
            "body_text": extract_plain_text(payload.get("payload")),
            "gmail_labels": payload.get("labelIds", []),
        }

    def list_labels(self):
        service = self.get_client()
        response = service.users().labels().list(userId="me").execute()
        return response.get("labels", [])

    def ensure_jobmail_labels(self):
        service = self.get_client()
        existing = {label["name"]: label["id"] for label in self.list_labels()}
        created = {}

        for name in LABELS:
            if name in existing:
                created[name] = existing[name]
                continue

            label = service.users().labels().create(
                userId="me",
                body={
                    "name": name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            ).execute()
            created[name] = label["id"]

        return created

    def add_label_to_message(self, message_id, label_id):
        service = self.get_client()
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label_id]},
        ).execute()

    def sync_messages(self, max_results=None):
        label_map = self.ensure_jobmail_labels()
        message_refs = self.list_messages(max_results=max_results)
        messages = []

        for ref in message_refs:
            try:
                messages.append(self.get_message(ref["id"]))
            except HttpError:
                continue

        return messages, label_map
