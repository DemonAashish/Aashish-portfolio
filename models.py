from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


def _split_lines(text):
    return [line.strip() for line in (text or "").split("\n") if line.strip()]


def _split_csv(text):
    return [item.strip() for item in (text or "").split(",") if item.strip()]


class AdminUser(UserMixin, db.Model):
    """The one account that can sign in to /dashboard."""

    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Education(db.Model):
    __tablename__ = "education"

    id = db.Column(db.Integer, primary_key=True)
    institution = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(200), nullable=False)
    date_range = db.Column(db.String(100))
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "institution": self.institution,
            "degree": self.degree,
            "date_range": self.date_range,
            "order": self.order,
        }


class Experience(db.Model):
    __tablename__ = "experience"

    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(200), nullable=False)
    date_range = db.Column(db.String(100))
    description = db.Column(db.Text)  # one bullet per line
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "date_range": self.date_range,
            "description": self.description or "",
            "highlights": _split_lines(self.description),
            "order": self.order,
        }


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    highlights = db.Column(db.Text)  # one bullet per line
    tech_stack = db.Column(db.String(300))  # comma separated
    github_url = db.Column(db.String(300))
    live_url = db.Column(db.String(300))
    featured = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "highlights_raw": self.highlights or "",
            "highlights": _split_lines(self.highlights),
            "tech_stack_raw": self.tech_stack or "",
            "tech_stack": _split_csv(self.tech_stack),
            "github_url": self.github_url or "",
            "live_url": self.live_url or "",
            "featured": bool(self.featured),
            "order": self.order,
        }


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "category": self.category, "order": self.order}


class Certification(db.Model):
    __tablename__ = "certifications"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    issuer = db.Column(db.String(200))
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "issuer": self.issuer or "",
            "description": self.description or "",
            "order": self.order,
        }


class Message(db.Model):
    """Contact form submissions."""

    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300))
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject or "",
            "body": self.body,
            "is_read": bool(self.is_read),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M UTC") if self.created_at else "",
        }


class ChatLog(db.Model):
    """Transcript of AI chat-widget conversations, for the dashboard."""

    __tablename__ = "chat_logs"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))
    user_message = db.Column(db.Text)
    ai_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_message": self.user_message,
            "ai_response": self.ai_response,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M UTC") if self.created_at else "",
        }
