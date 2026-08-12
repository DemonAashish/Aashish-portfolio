from flask import Blueprint, render_template

from models import Certification, Education, Experience, Project, Skill

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    projects = [p.to_dict() for p in Project.query.order_by(Project.order, Project.id).all()]
    experiences = [e.to_dict() for e in Experience.query.order_by(Experience.order, Experience.id).all()]
    education = [e.to_dict() for e in Education.query.order_by(Education.order, Education.id).all()]
    certifications = [c.to_dict() for c in Certification.query.order_by(Certification.order, Certification.id).all()]

    skills_by_category = {}
    for skill in Skill.query.order_by(Skill.category, Skill.order, Skill.id).all():
        skills_by_category.setdefault(skill.category, []).append(skill.name)

    return render_template(
        "index.html",
        projects=projects,
        experiences=experiences,
        education=education,
        certifications=certifications,
        skills_by_category=skills_by_category,
    )
