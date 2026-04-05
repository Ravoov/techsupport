# ⚡ SupportDesk — Tech Support Ticketing System

A two-part tech support system with a user-facing submission form and an admin dashboard, powered by SQLite (via sql.js).

## Features

- **User Form** (`/`) — Submit a ticket with username, email, and problem description
- **Admin Dashboard** (`/admin`) — View all tickets, respond to users, update ticket status
- **Email Integration** — Send emails directly via Gmail SMTP
- **SQLite Database** — All tickets stored in `db/support.db`
- **Auto-refresh** — Dashboard refreshes every 30 seconds

## Setup

### Prerequisites
- Node.js 16+

### Install & Run Locally

```bash
# Install dependencies
npm install

# Copy environment file and add your Gmail credentials
cp .env.example .env

# Start the server
npm start
```

Then open:
- **User Form:** http://localhost:3000/
- **Admin Dashboard:** http://localhost:3000/admin

## Deploying to Render

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set the build command: `npm install`
5. Set the start command: `npm start`
6. Add environment variables:
   - `GMAIL_USER` — Your Gmail address
   - `GMAIL_APP_PASSWORD` — Your Gmail App Password (see below)
   - `PORT` — Leave empty (Render sets this automatically)

### Gmail Setup for Email

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not already on
3. Go to "App passwords" and generate one for "Mail"
4. Add the 16-character password to your `.env` file or Render environment variables

## Running Dashboard Locally with Remote Server on Render

To run the admin dashboard locally while the server runs on Render:

1. Open `public/index.html` and `public/admin.html`
2. Find the `API_BASE` variable at the top of the `<script>` section:
   ```javascript
   const API_BASE = '';
   ```
3. Change it to your Render URL:
   ```javascript
   const API_BASE = 'https://your-app-name.onrender.com';
   ```
4. Open `public/admin.html` directly in your browser (double-click the file)

The dashboard will now fetch data from your Render server and send emails through it.

## How Email Works

When an admin clicks "Send Email to User":
1. The browser sends the ticket ID + solution text to the server
2. The server fetches the user's email from the database
3. The server sends an email directly via Gmail SMTP
4. The user's email address is never exposed to the admin dashboard

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tickets` | Submit a new ticket |
| GET | `/api/admin/tickets` | Get all tickets (no email field) |
| GET | `/api/admin/email-status` | Check if Gmail is configured |
| POST | `/api/admin/tickets/:id/send-email` | Send email to user |
| PATCH | `/api/admin/tickets/:id/status` | Update ticket status |

## Ticket Statuses
- `open` — New, unaddressed ticket
- `in_progress` — Being worked on
- `resolved` — Issue resolved
