# Aashish Upreti — Portfolio

A full-stack portfolio site built with **Flask + PostgreSQL**: a public single-page
portfolio, an admin **dashboard** that manages everything through a REST API
(the "frontend/backend interaction" layer), and an **AI chat widget** that answers
visitor questions using your own data as context.

## Stack

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Database:** PostgreSQL
- **Frontend:** Jinja2 templates + vanilla JS (fetch/AJAX) — no build step
- **AI chat:** Anthropic API (`claude-haiku-4-5` by default)

## Features

- Public portfolio (About, Experience, Projects, Skills, Certifications, Contact) — all content pulled live from Postgres
- Admin dashboard at `/dashboard` — full CRUD for Projects, Skills, Experience, Education, and Certifications, plus a Messages inbox and AI chat-log viewer, all driven by a JSON REST API (`routes/api.py`)
- AI chat widget on the public site, grounded on your live portfolio data so answers stay in sync with whatever you edit in the dashboard
- Contact form that saves submissions straight to Postgres
- Password-protected dashboard (change the password from the Account tab)

## Quick start (local)

**1. Install PostgreSQL** if you don't have it, then create a database:
```bash
createdb portfolio_db
```

**2. Set up the app:**
```bash
cd aashish-portfolio
python3 -m venv venv && source venv/bin/activate     # optional but recommended
pip install -r requirements.txt
cp .env.example .env
```

**3. Edit `.env`** — at minimum set `DATABASE_URL` to match your Postgres setup, and set `ADMIN_PASSWORD` to something real (not the default). Leave `ANTHROPIC_API_KEY` blank for now if you don't have one yet — everything except the chat widget will still work.

**4. Create tables and load your CV data:**
```bash
python seed_data.py
```

**5. Run it:**
```bash
python app.py
```
Visit `http://localhost:5000` for the site, `http://localhost:5000/dashboard` to log in and manage content.

## Quick start (Docker)

```bash
cp .env.example .env   # edit ADMIN_PASSWORD and ANTHROPIC_API_KEY at least
docker compose up --build
```
This starts Postgres and the app together and seeds the database automatically.

## Turning on the AI chat

1. Get a key at [console.anthropic.com](https://console.anthropic.com/) → Settings → API Keys.
2. Put it in `.env` as `ANTHROPIC_API_KEY=sk-ant-...`.
3. Restart the app. The chat widget (bottom-right on the public site) now answers using whatever's in your Projects/Experience/Skills/Education tables — edit those from the dashboard and the chatbot's answers update immediately, no retraining step.

Until a key is set, the widget stays fully functional in the UI but replies with a friendly "not configured yet" message instead of erroring.

## Project structure

```
app.py                 Flask app factory
config.py               Env-based configuration
models.py                SQLAlchemy models (Postgres tables)
seed_data.py              Creates tables + loads your CV data (safe to re-run)
routes/
  main.py                  Public homepage route
  auth.py                   Dashboard login/logout
  dashboard.py               Dashboard page shell
  api.py                      REST API: public (portfolio/contact/chat) + admin CRUD
services/
  ai_chat.py                 Builds chat context from Postgres, calls the Anthropic API
templates/                    Jinja2 templates (index, dashboard, login)
static/css, static/js          Styles + the vanilla-JS dashboard CRUD engine and chat widget
Dockerfile, docker-compose.yml  Optional containerized setup
```

## Editing content

- **Projects, Skills, Experience, Education, Certifications:** edit from `/dashboard` — no code changes needed.
- **Name, tagline, summary, and contact details in the hero/contact sections:** these are static text in `templates/index.html` (search for "Aashish" or your phone/email) since identity info like this rarely changes — just edit the HTML directly. There's also a `<!-- TODO -->` comment marking where to drop in your full LinkedIn URL.
- **Colors/fonts:** design tokens are CSS custom properties at the top of `static/css/main.css` (`--ink`, `--amber`, `--cyan`, etc.).

## Security notes before deploying publicly

This is a solid personal-project foundation, but before putting it on the open internet:
- Change `ADMIN_PASSWORD` and `SECRET_KEY` from their defaults (the app will warn you but won't stop you).
- Set `SESSION_COOKIE_SECURE=true` once you're serving over HTTPS.
- Consider adding CSRF protection (e.g. `Flask-WTF`) to the login and contact forms — the API endpoints validate input but don't currently include CSRF tokens.
- Consider rate-limiting `/api/chat` and `/api/contact` if you expect public traffic, to control AI API costs and spam.

## Deploying

Any host that gives you a Python process + Postgres works (Render, Railway, Fly.io, a VPS, etc.). The included `Dockerfile`/`docker-compose.yml` follow standard patterns for this. In short: set the same environment variables from `.env.example` on your host, run `python seed_data.py` once, then run the app with `gunicorn app:app` (already in `requirements.txt`).
