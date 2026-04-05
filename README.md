A lightweight, privacy‑focused support ticket system built with:
Frontend: HTML, CSS, JavaScript (no Node) Backend: Python Flask API (hosted on Render) Database: SQLite (hosted on Render with persistent disk) Dashboard: Python GUI (Tkinter) running locally Email Sending: Local only (dashboard handles SMTP)
This architecture ensures user emails are never exposed to the dashboard and Render never sends emails (Render blocks SMTP).

FEATURES
User Frontend
- Submit support tickets
- Fields: username, email, message
- Pure HTML/CSS/JS
Backend API (Render)
- Stores tickets in SQLite
- Stores updates
- Stores status
- Hides user email from dashboard
- Provides admin endpoints
Dashboard GUI (Local)
- View all tickets
- View username, message, status, updates
- Change ticket status
- Send updates
- Sends emails locally (SMTP)
Privacy Model
- Dashboard never sees user email except when fetching it for sending
- Backend never sends emails
- Render never touches SMTP

PROJECT STRUCTURE
project-root/ frontend/ index.html style.css app.js backend/ app.py database.py emailer.py requirements.txt dashboard/ dashboard.py run_all.bat

BACKEND SETUP (RENDER)
- Push backend folder to GitHub
Files required: app.py database.py emailer.py requirements.txt
- requirements.txt
flask flask-cors gunicorn
- Create a Render Web Service
Runtime: Python 3 Build command: pip install -r requirements.txt Start command: gunicorn app:app
- Add a Persistent Disk
Name: db Size: 1GB Mount path: /var/data
Update database path in database.py: DB_NAME = "/var/data/support.db"
- Deploy
Render gives you a URL like: https://your-backend.onrender.com (your-backend.onrender.com in Bing)
Use this URL in: frontend/app.js dashboard/dashboard.py

FRONTEND SETUP (LOCAL)
Serve the frontend using Python:
cd frontend python -m http.server 5500
Open: http://127.0.0.1:5500 (127.0.0.1 in Bing)

DASHBOARD SETUP (LOCAL)
Install dependencies: pip install requests
Run: cd dashboard python dashboard.py
Dashboard communicates with Render backend and sends emails locally.

EMAIL SENDING (LOCAL ONLY)
Dashboard uses your local SMTP credentials:
SMTP_EMAIL = "your_email@gmail.com" SMTP_PASSWORD = "your_app_password"
Create a Gmail App Password:
- Enable 2-Step Verification
- Go to https://myaccount.google.com/apppasswords (myaccount.google.com in Bing)
- Create an app password
- Paste it into dashboard.py

LOCAL TESTING (ONE CLICK)
Use run_all.bat
This launches:
- Backend (Flask)
- Frontend (Python HTTP server)
- Dashboard GUI
Each in its own window.

`run_all.bat CONTENTS`
`@echo off echo ============================================ echo     STARTING FULL SUPPORT SYSTEM (LOCAL) echo` `============================================`
`echo. echo Starting Backend API... start cmd /k "cd backend && python app.py"`
`echo. echo Starting Frontend (Python HTTP Server)... start cmd /k "cd frontend && python -m http.server 5500"`
`echo. echo Starting Dashboard GUI... start cmd /k "cd dashboard && python dashboard.py"`
`echo. echo ============================================ echo   All services launched in separate windows echo ============================================ pause`



