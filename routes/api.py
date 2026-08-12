from functools import wraps

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from extensions import db
from models import Certification, ChatLog, Education, Experience, Message, Project, Skill
from services.ai_chat import get_ai_response

api_bp = Blueprint("api", __name__)


def api_login_required(f):
    """Like Flask-Login's login_required, but returns JSON 401 instead of redirecting to /login.
    That matters here because these routes are called by fetch(), not a browser navigation."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required."}), 401
        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Public: aggregated portfolio data (also handy if you ever build another
# frontend against this same backend)
# ---------------------------------------------------------------------------

@api_bp.route("/portfolio")
def get_portfolio():
    projects = Project.query.order_by(Project.order, Project.id).all()
    experiences = Experience.query.order_by(Experience.order, Experience.id).all()
    education = Education.query.order_by(Education.order, Education.id).all()
    certifications = Certification.query.order_by(Certification.order, Certification.id).all()
    skills = Skill.query.order_by(Skill.category, Skill.order, Skill.id).all()

    return jsonify(
        {
            "projects": [p.to_dict() for p in projects],
            "experiences": [e.to_dict() for e in experiences],
            "education": [e.to_dict() for e in education],
            "certifications": [c.to_dict() for c in certifications],
            "skills": [s.to_dict() for s in skills],
        }
    )


# ---------------------------------------------------------------------------
# Public: contact form -> Postgres
# ---------------------------------------------------------------------------

@api_bp.route("/contact", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True) or request.form

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "").strip()
    body = (data.get("message") or "").strip()

    if not name or not email or not body:
        return jsonify({"error": "Name, email, and message are required."}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(body) > 5000:
        return jsonify({"error": "Message is too long."}), 400

    message = Message(name=name, email=email, subject=subject, body=body)
    db.session.add(message)
    db.session.commit()

    return jsonify({"success": True, "message": "Thanks for reaching out — I'll get back to you soon."})


# ---------------------------------------------------------------------------
# Public: AI chat widget
# ---------------------------------------------------------------------------

@api_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    session_id = (data.get("session_id") or "anonymous")[:100]

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(user_message) > 1000:
        return jsonify({"error": "Please keep messages under 1000 characters."}), 400

    reply = get_ai_response(user_message, session_id)
    return jsonify({"reply": reply})


# ---------------------------------------------------------------------------
# Admin: Projects
# ---------------------------------------------------------------------------

@api_bp.route("/admin/projects", methods=["GET", "POST"])
@api_login_required
def admin_projects():
    if request.method == "POST":
        data = request.get_json() or {}
        project = Project(
            title=data.get("title", ""),
            description=data.get("description", ""),
            highlights=data.get("highlights", ""),
            tech_stack=data.get("tech_stack", ""),
            github_url=data.get("github_url", ""),
            live_url=data.get("live_url", ""),
            featured=bool(data.get("featured", True)),
            order=int(data.get("order") or 0),
        )
        db.session.add(project)
        db.session.commit()
        return jsonify(project.to_dict()), 201

    projects = Project.query.order_by(Project.order, Project.id).all()
    return jsonify([p.to_dict() for p in projects])


@api_bp.route("/admin/projects/<int:project_id>", methods=["PUT", "DELETE"])
@api_login_required
def admin_project_detail(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"error": "Not found."}), 404

    if request.method == "DELETE":
        db.session.delete(project)
        db.session.commit()
        return jsonify({"success": True})

    data = request.get_json() or {}
    for field in ("title", "description", "highlights", "tech_stack", "github_url", "live_url"):
        if field in data:
            setattr(project, field, data[field])
    if "featured" in data:
        project.featured = bool(data["featured"])
    if "order" in data:
        project.order = int(data["order"] or 0)

    db.session.commit()
    return jsonify(project.to_dict())


# ---------------------------------------------------------------------------
# Admin: Skills
# ---------------------------------------------------------------------------

@api_bp.route("/admin/skills", methods=["GET", "POST"])
@api_login_required
def admin_skills():
    if request.method == "POST":
        data = request.get_json() or {}
        skill = Skill(
            name=data.get("name", ""),
            category=data.get("category", ""),
            order=int(data.get("order") or 0),
        )
        db.session.add(skill)
        db.session.commit()
        return jsonify(skill.to_dict()), 201

    skills = Skill.query.order_by(Skill.category, Skill.order, Skill.id).all()
    return jsonify([s.to_dict() for s in skills])


@api_bp.route("/admin/skills/<int:skill_id>", methods=["PUT", "DELETE"])
@api_login_required
def admin_skill_detail(skill_id):
    skill = db.session.get(Skill, skill_id)
    if not skill:
        return jsonify({"error": "Not found."}), 404

    if request.method == "DELETE":
        db.session.delete(skill)
        db.session.commit()
        return jsonify({"success": True})

    data = request.get_json() or {}
    for field in ("name", "category"):
        if field in data:
            setattr(skill, field, data[field])
    if "order" in data:
        skill.order = int(data["order"] or 0)

    db.session.commit()
    return jsonify(skill.to_dict())


# ---------------------------------------------------------------------------
# Admin: Experience
# ---------------------------------------------------------------------------

@api_bp.route("/admin/experience", methods=["GET", "POST"])
@api_login_required
def admin_experience():
    if request.method == "POST":
        data = request.get_json() or {}
        experience = Experience(
            company=data.get("company", ""),
            role=data.get("role", ""),
            date_range=data.get("date_range", ""),
            description=data.get("description", ""),
            order=int(data.get("order") or 0),
        )
        db.session.add(experience)
        db.session.commit()
        return jsonify(experience.to_dict()), 201

    experiences = Experience.query.order_by(Experience.order, Experience.id).all()
    return jsonify([e.to_dict() for e in experiences])


@api_bp.route("/admin/experience/<int:exp_id>", methods=["PUT", "DELETE"])
@api_login_required
def admin_experience_detail(exp_id):
    experience = db.session.get(Experience, exp_id)
    if not experience:
        return jsonify({"error": "Not found."}), 404

    if request.method == "DELETE":
        db.session.delete(experience)
        db.session.commit()
        return jsonify({"success": True})

    data = request.get_json() or {}
    for field in ("company", "role", "date_range", "description"):
        if field in data:
            setattr(experience, field, data[field])
    if "order" in data:
        experience.order = int(data["order"] or 0)

    db.session.commit()
    return jsonify(experience.to_dict())


# ---------------------------------------------------------------------------
# Admin: Education
# ---------------------------------------------------------------------------

@api_bp.route("/admin/education", methods=["GET", "POST"])
@api_login_required
def admin_education():
    if request.method == "POST":
        data = request.get_json() or {}
        education = Education(
            institution=data.get("institution", ""),
            degree=data.get("degree", ""),
            date_range=data.get("date_range", ""),
            order=int(data.get("order") or 0),
        )
        db.session.add(education)
        db.session.commit()
        return jsonify(education.to_dict()), 201

    education = Education.query.order_by(Education.order, Education.id).all()
    return jsonify([e.to_dict() for e in education])


@api_bp.route("/admin/education/<int:edu_id>", methods=["PUT", "DELETE"])
@api_login_required
def admin_education_detail(edu_id):
    education = db.session.get(Education, edu_id)
    if not education:
        return jsonify({"error": "Not found."}), 404

    if request.method == "DELETE":
        db.session.delete(education)
        db.session.commit()
        return jsonify({"success": True})

    data = request.get_json() or {}
    for field in ("institution", "degree", "date_range"):
        if field in data:
            setattr(education, field, data[field])
    if "order" in data:
        education.order = int(data["order"] or 0)

    db.session.commit()
    return jsonify(education.to_dict())


# ---------------------------------------------------------------------------
# Admin: Certifications
# ---------------------------------------------------------------------------

@api_bp.route("/admin/certifications", methods=["GET", "POST"])
@api_login_required
def admin_certifications():
    if request.method == "POST":
        data = request.get_json() or {}
        certification = Certification(
            name=data.get("name", ""),
            issuer=data.get("issuer", ""),
            description=data.get("description", ""),
            order=int(data.get("order") or 0),
        )
        db.session.add(certification)
        db.session.commit()
        return jsonify(certification.to_dict()), 201

    certifications = Certification.query.order_by(Certification.order, Certification.id).all()
    return jsonify([c.to_dict() for c in certifications])


@api_bp.route("/admin/certifications/<int:cert_id>", methods=["PUT", "DELETE"])
@api_login_required
def admin_certification_detail(cert_id):
    certification = db.session.get(Certification, cert_id)
    if not certification:
        return jsonify({"error": "Not found."}), 404

    if request.method == "DELETE":
        db.session.delete(certification)
        db.session.commit()
        return jsonify({"success": True})

    data = request.get_json() or {}
    for field in ("name", "issuer", "description"):
        if field in data:
            setattr(certification, field, data[field])
    if "order" in data:
        certification.order = int(data["order"] or 0)

    db.session.commit()
    return jsonify(certification.to_dict())


# ---------------------------------------------------------------------------
# Admin: Messages (read-only status flag + delete)
# ---------------------------------------------------------------------------

@api_bp.route("/admin/messages", methods=["GET"])
@api_login_required
def admin_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages])


@api_bp.route("/admin/messages/<int:msg_id>", methods=["PATCH", "DELETE"])
@api_login_required
def admin_message_detail(msg_id):
    message = db.session.get(Message, msg_id)
    if not message:
        return jsonify({"error": "Not found."}), 404

    if request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        return jsonify({"success": True})

    data = request.get_json() or {}
    if "is_read" in data:
        message.is_read = bool(data["is_read"])
    db.session.commit()
    return jsonify(message.to_dict())


# ---------------------------------------------------------------------------
# Admin: Chat logs (read-only)
# ---------------------------------------------------------------------------

@api_bp.route("/admin/chatlogs", methods=["GET"])
@api_login_required
def admin_chatlogs():
    logs = ChatLog.query.order_by(ChatLog.created_at.desc()).limit(200).all()
    return jsonify([c.to_dict() for c in logs])


# ---------------------------------------------------------------------------
# Admin: dashboard overview stats
# ---------------------------------------------------------------------------

@api_bp.route("/admin/stats", methods=["GET"])
@api_login_required
def admin_stats():
    return jsonify(
        {
            "projects": Project.query.count(),
            "skills": Skill.query.count(),
            "messages": Message.query.count(),
            "unread_messages": Message.query.filter_by(is_read=False).count(),
            "chat_conversations": ChatLog.query.count(),
        }
    )


# ---------------------------------------------------------------------------
# Admin: account / password
# ---------------------------------------------------------------------------

@api_bp.route("/admin/account/password", methods=["PATCH"])
@api_login_required
def change_password():
    data = request.get_json() or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_user.check_password(current_password):
        return jsonify({"error": "Current password is incorrect."}), 400
    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters."}), 400

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"success": True, "message": "Password updated."})
