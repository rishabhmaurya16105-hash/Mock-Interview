# Mock Interview

AI-powered mock interview app for resume-based question generation and scoring.

## Prerequisites

- Node.js LTS
- Python 3.11+
- Git

## Required Environment Variables

### Frontend

Copy `frontend/.env.example` to `frontend/.env`.

Required variable:

- `VITE_API_URL=http://localhost:8000`

### Backend

Copy `backend/.env.example` to `backend/.env`.

Required variables:

- `SECRET_KEY=django-insecure-change-me`
- `DEBUG=True`
- `AI_SERVICE_URL=http://127.0.0.1:8001`

### AI Service

Copy `ai-service/.env.example` to `ai-service/.env`.

Required variables:

- `GROQ_API_KEY=your_groq_api_key_here`
- `GROQ_MODEL=llama-3.1-8b-instant`

## How To Run Backend

```powershell
cd "c:\Users\Rishabh\@@@\mock-interview\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver
```

Optional Django admin setup:

```powershell
cd "c:\Users\Rishabh\@@@\mock-interview\backend"
.\venv\Scripts\python.exe manage.py createsuperuser
```

## How To Run AI Service

```powershell
cd "c:\Users\Rishabh\@@@\mock-interview\ai-service"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
.\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8001
```

## How To Run Frontend

```powershell
cd "c:\Users\Rishabh\@@@\mock-interview\frontend"
copy .env.example .env
npm install
npm run dev
```

## Docker Setup

`docker-compose.yml` runs the current project with SQLite persistence through the mounted `backend` folder, so `db.sqlite3` stays available across container restarts.

Before starting Docker, make sure these files exist:

- `backend/.env`
- `ai-service/.env`

Run:

```powershell
cd "c:\Users\Rishabh\@@@\mock-interview"
docker compose up --build
```

Services:

- Django backend: `http://localhost:8000`
- FastAPI AI service: `http://localhost:8001/health`
