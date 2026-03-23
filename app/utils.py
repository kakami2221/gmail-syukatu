import base64
import re
from datetime import datetime, timezone
from email.utils import parseaddr

from bs4 import BeautifulSoup


COMPANY_SUFFIX_PATTERN = re.compile(
    r"(株式会社|有限会社|合同会社|Inc\.?|Co\.,?\s*Ltd\.?|LLC|Corp\.?|採用担当|採用事務局)"
)


def decode_base64url(data):
    if not data:
        return ""
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode(
        "utf-8", errors="ignore"
    )


def extract_plain_text(payload):
    if not payload:
        return ""

    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})

    if mime_type == "text/plain":
        return decode_base64url(body.get("data"))

    if mime_type == "text/html":
        html = decode_base64url(body.get("data"))
        return BeautifulSoup(html, "html.parser").get_text("\n", strip=True)

    for part in payload.get("parts", []) or []:
        text = extract_plain_text(part)
        if text:
            return text

    return ""


def parse_gmail_datetime(internal_date_ms):
    if not internal_date_ms:
        return None
    return datetime.fromtimestamp(int(internal_date_ms) / 1000, tz=timezone.utc)


def extract_sender_parts(sender):
    name, email_addr = parseaddr(sender or "")
    return name.strip(), email_addr.strip().lower()


def normalize_company_name(value):
    text = value or ""
    text = COMPANY_SUFFIX_PATTERN.sub("", text)
    text = re.sub(r"[【】\[\]<>「」『』()（）]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "不明"


def infer_company_name(sender_name, subject, body_text):
    candidates = []

    if sender_name:
        candidates.append(sender_name)

    subject_match = re.search(r"[【\[]?(.+?)(株式会社|有限会社|Inc\.?|Co\.)", subject or "")
    if subject_match:
        candidates.append(subject_match.group(1))

    bureau_match = re.search(r"(.+?)(採用担当|採用事務局)", sender_name or "")
    if bureau_match:
        candidates.append(bureau_match.group(1))

    body_match = re.search(r"(株式会社\s*[\w一-龠ぁ-んァ-ヶー]+)", body_text or "")
    if body_match:
        candidates.append(body_match.group(1))

    for candidate in candidates:
        normalized = normalize_company_name(candidate)
        if normalized and normalized != "不明":
            return normalized

    return "不明"
