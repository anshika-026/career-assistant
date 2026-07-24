# AI-Powered Career Assistant

Full-stack app: upload a resume, get an ATS readiness score, match it against
a job description to find skill gaps, generate tailored interview questions,
and get learning recommendations for what's missing. Django REST API backend
+ a plain HTML/CSS/JS frontend (no build step required).

## Stack
- **Backend:** Django 4.2 (LTS) + Django REST Framework, JWT auth (SimpleJWT)
- **Database:** PostgreSQL
- **Parsing:** pdfplumber (PDF), python-docx (DOCX)
- **AI:** Google Gemini API for interview questions + learning recommendations
  (falls back to rule-based output if no API key is set, so the app fully
  works without one)
- **Frontend:** vanilla HTML/CSS/JS served directly by Django (no React/Node
  build step)
- **Async (optional):** Celery + Redis, scaffolded but not required to run

## Project layout
```
career_assistant/     # Django settings, root urls, celery config
accounts/              # custom User model, JWT register/login
resumes/                # upload + PDF/DOCX text extraction
analysis/               # ATS scoring + skill extraction + email notification
jobs/                   # job descriptions + resume-to-job matching
ai_engine/               # Gemini-powered interview questions & recommendations
dashboard/               # analytics summary endpoint
frontend/                # HTML templates + views serving the UI
static/frontend/         # CSS/JS for the UI
```

## Setup

1. **Virtual environment + dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **PostgreSQL**
   ```sql
   CREATE DATABASE career_assistant_db;
   CREATE USER postgres WITH PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE career_assistant_db TO postgres;
   ```

3. **Environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env`: set `DJANGO_SECRET_KEY`, your DB credentials, and (optionally)
   `GEMINI_API_KEY` for real AI-generated interview questions / recommendations.
   Get a free key at https://aistudio.google.com (no credit card required).
   Without that key, the app still works using built-in rule-based fallbacks.

   Django doesn't auto-load `.env` files. Either export the variables in your
   shell, or add this to the very top of `career_assistant/settings.py`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

4. **Migrate + create an admin user**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run it**
   ```bash
   python manage.py runserver
   ```
   - Frontend: http://localhost:8000/login/
   - Admin panel: http://localhost:8000/admin/
   - API root: http://localhost:8000/api/

## Using the app
1. Sign up at `/login/` (there's a "create one" link).
2. **Resume tab:** upload a PDF or DOCX. It's parsed and ATS-scored automatically.
3. **ATS Score tab:** see the score, detected skills, and specific issues to fix.
4. **Job Match tab:** paste a job description, run a match, see matched vs.
   missing skills.
5. **Interview tab:** generate interview questions tailored to your resume
   (and the matched job, if you ran one).
6. **Learn tab:** from a job match, click "Get learning recommendations" to
   see what to study for the skills you're missing.

Every analysis triggers a console-logged "email" (dev email backend just
prints to your terminal — check the terminal running `runserver`).

## API reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create account, returns JWT tokens |
| POST | `/api/auth/login/` | Login, returns JWT tokens |
| POST | `/api/auth/login/refresh/` | Refresh an access token |
| GET | `/api/auth/me/` | Current user + profile |
| GET/POST | `/api/resumes/` | List / upload resumes (parsed on upload) |
| GET/DELETE | `/api/resumes/<id>/` | Retrieve / delete a resume |
| POST | `/api/resumes/<id>/reparse/` | Re-run text extraction |
| GET | `/api/analysis/` | List past ATS analyses |
| GET | `/api/analysis/<id>/` | One analysis result |
| POST | `/api/analysis/analyze/<resume_id>/` | Run ATS scoring on a resume |
| GET/POST | `/api/jobs/` | List / save job descriptions |
| GET/DELETE | `/api/jobs/<id>/` | Retrieve / delete a job description |
| POST | `/api/jobs/<job_id>/match/<resume_id>/` | Match a resume to a job |
| GET | `/api/jobs/matches/` | List past job matches |
| POST | `/api/ai/interview-questions/<resume_id>/` | Generate interview questions (optional body: `{"job_id": N}`) |
| GET | `/api/ai/interview-questions/` | List past interview sessions |
| POST | `/api/ai/learning-recommendations/<job_match_id>/` | Generate recs for a match's skill gap |
| GET | `/api/ai/learning-recommendations/` | List past recommendations |
| GET | `/api/dashboard/summary/` | Aggregated stats for the dashboard |

All endpoints except register/login require `Authorization: Bearer <access_token>`.

## Notes on design choices
- **ATS scoring is rule-based, not ML.** It checks for standard resume
  sections, contact info, keyword/skill density, and length — the same kind
  of heuristics real ATS systems use. This keeps it fast, free, and fully
  explainable (the `issues` list tells you exactly why a score is what it is).
- **Skill extraction is a shared module** (`analysis/scoring.py`) used by
  both resume analysis and job matching, so a skill recognized in one place
  is recognized consistently in the other. Extend `analysis/skills_data.py`
  to add more skills/categories.
- **AI features degrade gracefully.** If `GEMINI_API_KEY` isn't set,
  `ai_engine/claude_client.py` falls back to a varied bank of realistic,
  skill-specific template questions and recommendations instead of failing.
- **Email is synchronous by default** via Django's console backend (prints to
  terminal). `career_assistant/celery.py` is scaffolded if you want to move
  email/AI calls to a background worker later — not required to run the app.


