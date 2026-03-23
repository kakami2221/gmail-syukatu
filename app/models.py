from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )


class Company(TimestampMixin, db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    normalized_name = db.Column(db.String(255), nullable=False, unique=True, index=True)
    latest_received_at = db.Column(db.DateTime(timezone=True))
    current_stage = db.Column(db.String(120), default="不明", nullable=False)

    emails = db.relationship("Email", back_populates="company", lazy="dynamic")
    threads = db.relationship("Thread", back_populates="company", lazy="dynamic")


class Thread(TimestampMixin, db.Model):
    __tablename__ = "threads"

    id = db.Column(db.Integer, primary_key=True)
    gmail_thread_id = db.Column(db.String(255), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    latest_subject = db.Column(db.String(500))
    latest_received_at = db.Column(db.DateTime(timezone=True))
    mail_count = db.Column(db.Integer, default=0, nullable=False)
    has_action_required = db.Column(db.Boolean, default=False, nullable=False)
    stage_estimate = db.Column(db.String(120), default="不明", nullable=False)

    __table_args__ = (
        db.UniqueConstraint("gmail_thread_id", "company_id", name="uq_thread_company"),
    )

    company = db.relationship("Company", back_populates="threads")
    emails = db.relationship("Email", back_populates="thread", lazy="dynamic")


class Email(TimestampMixin, db.Model):
    __tablename__ = "emails"

    id = db.Column(db.Integer, primary_key=True)
    gmail_message_id = db.Column(db.String(255), nullable=False, unique=True, index=True)
    gmail_thread_id = db.Column(db.String(255), nullable=False, index=True)
    subject = db.Column(db.String(500), nullable=False, default="")
    sender = db.Column(db.String(255), nullable=False, default="")
    sender_email = db.Column(db.String(255), nullable=False, default="")
    body_text = db.Column(db.Text, nullable=False, default="")
    snippet = db.Column(db.Text, nullable=False, default="")
    received_at = db.Column(db.DateTime(timezone=True), index=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"))
    thread_id = db.Column(db.Integer, db.ForeignKey("threads.id"))
    category = db.Column(db.String(120), nullable=False, default="就活/その他")
    gmail_labels = db.Column(db.Text, nullable=False, default="")
    is_job_related = db.Column(db.Boolean, default=False, nullable=False)

    company = db.relationship("Company", back_populates="emails")
    thread = db.relationship("Thread", back_populates="emails")
