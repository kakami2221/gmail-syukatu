from .models import Company, Thread, db
from .utils import infer_company_name, normalize_company_name


STAGE_PRIORITY = [
    ("合否通知", ["就活/合否"]),
    ("最終面接", ["最終面接"]),
    ("二次面接", ["二次面接"]),
    ("一次面接", ["一次面接", "就活/面接"]),
    ("適性検査", ["就活/適性検査"]),
    ("ES提出", ["就活/ES"]),
    ("説明会", ["就活/説明会"]),
    ("エントリー受付", ["エントリー", "就活/要確認"]),
]


def get_or_create_company(email_data):
    name = infer_company_name(
        email_data["sender_name"],
        email_data["subject"],
        email_data["body_text"],
    )
    normalized = normalize_company_name(name)

    company = Company.query.filter_by(normalized_name=normalized).first()
    if company:
        return company

    company = Company(name=name, normalized_name=normalized)
    db.session.add(company)
    db.session.flush()
    return company


def estimate_stage(emails):
    joined = " ".join(
        filter(None, [f"{mail.subject} {mail.body_text} {mail.category}" for mail in emails])
    )

    for stage, markers in STAGE_PRIORITY:
        if any(marker in joined for marker in markers):
            return stage

    return "不明"


def rebuild_thread_for_company(company, gmail_thread_id):
    emails = (
        company.emails.filter_by(gmail_thread_id=gmail_thread_id)
        .order_by(db.text("received_at asc"))
        .all()
    )
    if not emails:
        return None

    latest_email = max(emails, key=lambda item: item.received_at or item.created_at)
    has_action_required = any(mail.category == "就活/要返信" for mail in emails)
    stage_estimate = estimate_stage(emails)

    thread = Thread.query.filter_by(
        company_id=company.id, gmail_thread_id=gmail_thread_id
    ).first()
    if thread is None:
        thread = Thread(company_id=company.id, gmail_thread_id=gmail_thread_id)
        db.session.add(thread)

    thread.latest_subject = latest_email.subject
    thread.latest_received_at = latest_email.received_at
    thread.mail_count = len(emails)
    thread.has_action_required = has_action_required
    thread.stage_estimate = stage_estimate

    for email in emails:
        email.thread = thread

    company.latest_received_at = latest_email.received_at
    company.current_stage = stage_estimate
    return thread
