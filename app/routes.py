from flask import Blueprint, current_app, redirect, render_template, url_for
from sqlalchemy import func

from .classifier import classify_email
from .gmail_service import GmailService
from .models import Company, Email, Thread, db
from .thread_builder import get_or_create_company, rebuild_thread_for_company


bp = Blueprint("main", __name__)


def sync_gmail_to_db():
    service = GmailService(current_app)
    messages, label_map = service.sync_messages(
        max_results=current_app.config["MAIL_FETCH_MAX_RESULTS"]
    )

    for item in messages:
        existing = Email.query.filter_by(gmail_message_id=item["gmail_message_id"]).first()
        category = classify_email(item["sender"], item["subject"], item["body_text"])
        is_job_related = category != "就活/その他"

        if existing:
            email = existing
        else:
            email = Email(gmail_message_id=item["gmail_message_id"])
            db.session.add(email)

        company = get_or_create_company(item) if is_job_related else None

        email.gmail_thread_id = item["gmail_thread_id"]
        email.subject = item["subject"]
        email.sender = item["sender"]
        email.sender_email = item["sender_email"]
        email.body_text = item["body_text"]
        email.snippet = item["snippet"]
        email.received_at = item["received_at"]
        email.category = category
        email.gmail_labels = ",".join(item["gmail_labels"])
        email.is_job_related = is_job_related
        email.company = company

        if category in label_map:
            try:
                service.add_label_to_message(email.gmail_message_id, label_map[category])
            except Exception:
                pass

        if company:
            rebuild_thread_for_company(company, email.gmail_thread_id)

    db.session.commit()


@bp.route("/")
def dashboard():
    stats = {
        "unprocessed_count": Email.query.filter_by(category="就活/要確認").count(),
        "reply_count": Email.query.filter_by(category="就活/要返信").count(),
        "company_count": Company.query.count(),
        "new_count": Email.query.order_by(Email.received_at.desc()).limit(10).count(),
    }
    label_counts = (
        db.session.query(Email.category, func.count(Email.id))
        .group_by(Email.category)
        .order_by(func.count(Email.id).desc())
        .all()
    )
    latest_emails = Email.query.order_by(Email.received_at.desc()).limit(10).all()
    return render_template(
        "dashboard.html",
        stats=stats,
        label_counts=label_counts,
        latest_emails=latest_emails,
    )


@bp.route("/emails")
def emails():
    items = Email.query.order_by(Email.received_at.desc()).all()
    return render_template("emails.html", emails=items)


@bp.route("/emails/<int:email_id>")
def email_detail(email_id):
    email = Email.query.get_or_404(email_id)
    return render_template("email_detail.html", email=email)


@bp.route("/companies")
def companies():
    items = Company.query.order_by(Company.latest_received_at.desc()).all()
    return render_template("companies.html", companies=items)


@bp.route("/companies/<int:company_id>")
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    emails = company.emails.order_by(Email.received_at.desc()).all()
    threads = company.threads.order_by(Thread.latest_received_at.desc()).all()
    return render_template(
        "company_detail.html",
        company=company,
        emails=emails,
        threads=threads,
    )


@bp.route("/sync")
def sync():
    sync_gmail_to_db()
    return redirect(url_for("main.dashboard"))
