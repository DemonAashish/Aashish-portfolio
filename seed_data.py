"""
Creates all tables and populates them with Aashish's CV data, plus the admin
account used to log in to /dashboard.

Usage:
    python seed_data.py

Safe to re-run: each section only inserts if that table is still empty, so it
won't duplicate rows or overwrite edits you've made from the dashboard.
"""

from app import create_app
from config import Config
from extensions import db
from models import AdminUser, Certification, Education, Experience, Project, Skill

app = create_app()

with app.app_context():
    db.create_all()

    # --- Admin account ------------------------------------------------
    if not AdminUser.query.filter_by(username=Config.ADMIN_USERNAME).first():
        admin = AdminUser(username=Config.ADMIN_USERNAME)
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        print(f"Created admin user '{Config.ADMIN_USERNAME}' — change this password from the dashboard after first login.")

    # --- Education ------------------------------------------------------
    if not Education.query.first():
        db.session.add_all(
            [
                Education(
                    institution="Kathmandu Engineering College (IOE)",
                    degree="Bachelor in Computer Engineering (BE)",
                    date_range="2015 - 2021",
                    order=1,
                ),
                Education(
                    institution="University of Greenwich, UK",
                    degree="MSc Data Science",
                    date_range="2024 - 2025",
                    order=2,
                ),
            ]
        )
        print("Seeded education.")

    # --- Experience -------------------------------------------------------
    if not Experience.query.first():
        db.session.add_all(
            [
                Experience(
                    company="Soori Technologies",
                    role="Software Developer",
                    date_range="July 2023 - Sep 2024",
                    description=(
                        "Collaborated with the team to design, develop, implement, and optimize "
                        "automated pipelines for seamless software integration.\n"
                        "Partnered with cross-functional teams to embed robust DevOps practices "
                        "into the development lifecycle, with a strong emphasis on CI/CD."
                    ),
                    order=1,
                ),
                Experience(
                    company="Amnil Technologies",
                    role="Frontend Developer",
                    date_range="Sept 2022 - Apr 2023",
                    description=(
                        "Contributed to the development and deployment of Track, Trace, and "
                        "Paperless solutions for government organizations, banks, hospitals, "
                        "and corporate houses."
                    ),
                    order=2,
                ),
            ]
        )
        print("Seeded experience.")

    # --- Projects -----------------------------------------------------
    if not Project.query.first():
        db.session.add(
            Project(
                title="YATRA — Real-Time Public Transport Tracking System",
                description=(
                    "An Android application integrating the Google Maps API to stream real-time "
                    "GPS data, giving commuters live vehicle locations across selected transit routes."
                ),
                highlights=(
                    "Engineered location-matching features to detect the nearest bus stop and "
                    "calculate shortest-path routing for commuters to optimize boarding efficiency.\n"
                    "Architected the system to support future Machine Learning integrations, "
                    "establishing a data foundation for predictive ETA modeling and anomaly "
                    "detection for irregular route delays."
                ),
                tech_stack="Android, Google Maps API, GPS, Java/Kotlin",
                featured=True,
                order=1,
            )
        )
        print("Seeded projects. Add more any time from the dashboard.")

    # --- Skills ---------------------------------------------------------
    if not Skill.query.first():
        skills_by_category = {
            "Programming Languages": ["Python", "SQL", "R", "JavaScript"],
            "Data Science, AI & ML": [
                "Pandas", "NumPy", "Scikit-learn", "LangChain", "Power BI",
                "Matplotlib", "Seaborn", "NLP", "LLMs/AI Agents", "Predictive Analytics",
            ],
            "Cloud, DevOps & MLOps": ["AWS", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "CI/CD Pipelines"],
            "Databases": ["MySQL", "MongoDB", "Microsoft SQL Server", "Query Optimization", "PostgreSQL"],
            "Python Dev & Frameworks": ["Django", "FastAPI", "Flask", "RESTful API Design", "Unit Testing (PyTest)"],
        }
        order = 0
        for category, names in skills_by_category.items():
            for name in names:
                order += 1
                db.session.add(Skill(name=name, category=category, order=order))
        print("Seeded skills.")

    # --- Certifications -------------------------------------------------
    if not Certification.query.first():
        db.session.add_all(
            [
                Certification(
                    name="Fundamentals of Building AI Agents",
                    issuer="IBM",
                    description=(
                        "Foundational knowledge in designing and implementing autonomous AI "
                        "agents. Explored LLMs, agentic workflows, and integrating AI systems "
                        "with external tools and APIs."
                    ),
                    order=1,
                ),
                Certification(
                    name="Python for Data Science, AI & Development",
                    issuer="IBM",
                    description="Hands-on experience in data manipulation and statistical analysis using Pandas and NumPy.",
                    order=2,
                ),
                Certification(
                    name="Developing AI Applications With Python & Flask",
                    issuer="IBM",
                    description="Built and deployed web applications using Flask for routing, server-side logic, and API integration.",
                    order=3,
                ),
            ]
        )
        print("Seeded certifications.")

    db.session.commit()
    print("\nDatabase ready.")
