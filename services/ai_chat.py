"""
Powers the chat widget on the public site.

On every message we pull the current portfolio content straight out of Postgres
and hand it to Claude as system-prompt context, so the assistant's answers stay
in sync with whatever's been edited in the dashboard -- no separate "retraining"
step needed.
"""

from anthropic import Anthropic, APIError

from config import Config
from extensions import db
from models import Certification, ChatLog, Education, Experience, Project, Skill

_client = None
_client_checked = False


def _get_client():
    """Lazily build the Anthropic client. Returns None if no API key is configured,
    so the rest of the app keeps working (with a friendly fallback message)
    even before ANTHROPIC_API_KEY is set."""
    global _client, _client_checked
    if not _client_checked:
        _client_checked = True
        if Config.ANTHROPIC_API_KEY:
            _client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    return _client


def _build_system_prompt():
    experiences = Experience.query.order_by(Experience.order, Experience.id).all()
    education = Education.query.order_by(Education.order, Education.id).all()
    projects = Project.query.order_by(Project.order, Project.id).all()
    certifications = Certification.query.order_by(Certification.order, Certification.id).all()
    skills = Skill.query.order_by(Skill.category, Skill.order, Skill.id).all()

    skills_by_category = {}
    for skill in skills:
        skills_by_category.setdefault(skill.category, []).append(skill.name)

    lines = [
        f"You are the AI assistant embedded on {Config.SITE_OWNER_NAME}'s personal portfolio "
        "website. You help visitors (recruiters, hiring managers, collaborators) learn about "
        "his background using ONLY the facts listed below. Speak about him in the third person. "
        "Be warm, concise (usually 2-4 sentences), and specific. If something isn't covered "
        "below, say you don't have that detail rather than guessing, and suggest the visitor "
        "use the contact form. If asked about something unrelated to his professional "
        "background, politely steer the conversation back.",
        "",
        "=== WORK EXPERIENCE ===",
    ]
    for exp in experiences:
        lines.append(f"- {exp.role} at {exp.company} ({exp.date_range}). {exp.description}".replace("\n", " "))

    lines.append("\n=== EDUCATION ===")
    for edu in education:
        lines.append(f"- {edu.degree}, {edu.institution} ({edu.date_range})")

    lines.append("\n=== PROJECTS ===")
    for proj in projects:
        tech = f" Tech stack: {proj.tech_stack}." if proj.tech_stack else ""
        lines.append(f"- {proj.title}: {proj.description}{tech}".replace("\n", " "))

    lines.append("\n=== SKILLS ===")
    for category, names in skills_by_category.items():
        lines.append(f"- {category}: {', '.join(names)}")

    lines.append("\n=== CERTIFICATIONS ===")
    for cert in certifications:
        lines.append(f"- {cert.name} ({cert.issuer})")

    return "\n".join(lines)


def get_ai_response(user_message: str, session_id: str) -> str:
    client = _get_client()

    if client is None:
        reply = (
            "The AI chat isn't fully wired up yet — whoever owns this site needs to add an "
            "ANTHROPIC_API_KEY to the .env file. In the meantime, feel free to browse the "
            "Experience and Projects sections above!"
        )
        _log_chat(session_id, user_message, reply)
        return reply

    try:
        response = client.messages.create(
            model=Config.AI_MODEL,
            max_tokens=400,
            system=_build_system_prompt(),
            messages=[{"role": "user", "content": user_message}],
        )
        reply = "".join(block.text for block in response.content if block.type == "text").strip()
        if not reply:
            reply = "Sorry, I couldn't quite come up with a response to that — could you rephrase?"
    except APIError:
        reply = "Sorry, I'm having trouble reaching the AI service right now. Please try again in a moment."
    except Exception:
        reply = "Something went wrong on my end — please try again in a moment."

    _log_chat(session_id, user_message, reply)
    return reply


def _log_chat(session_id: str, user_message: str, reply: str) -> None:
    try:
        db.session.add(ChatLog(session_id=session_id, user_message=user_message, ai_response=reply))
        db.session.commit()
    except Exception:
        db.session.rollback()
