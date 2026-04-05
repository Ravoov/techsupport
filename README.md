# Customer Support Ticket System

A full-stack customer support ticket management system with a web frontend for customers, a REST API backend, and a GUI dashboard for support staff to manage tickets and communicate with customers.

## Project Structure

```
techsupport/
├── frontend/              # Web UI for customers
│   ├── index.html        # Main form page
│   ├── app.js            # Frontend logic
│   └── style.css         # Styling
├── backend/              # Flask REST API
│   ├── app.py            # Main API server
│   └── database.py       # SQLite database functions
├── dashboard/            # Support staff GUI interface
│   └── dashboard.py      # Tkinter admin dashboard
├── run.bat               # Startup script
└── README.md             # This file
```

## Features

### Customer Portal (Frontend)
- Submit support tickets with username, email, and message
- Receive instant ticket ID confirmation
- Clean, simple web interface

### Admin Dashboard
- View all support tickets in a list
- Click tickets to view full details and update history
- Change ticket status (open → in-progress → closed)
- Send updates to customers via email
- Real-time ticket updates

### Backend API
REST endpoints for ticket management:
- `POST /support/request` - Create new support ticket
- `GET /admin/tickets` - List all tickets (admin only)
- `GET /admin/ticket/<ticket_id>` - Get ticket details with updates
- `POST /admin/update` - Add message update to ticket
- `POST /admin/status` - Change ticket status
- `GET /admin/email/<ticket_id>` - Get customer email

### Database
SQLite database with two tables:
- **tickets** - Stores ticket info (id, email, username, message, status)
- **updates** - Stores communication history with timestamps

## Setup & Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Install dependencies:**
   ```bash
   pip install flask flask-cors requests
   ```

2. **Configure email (optional):**
   - Edit `dashboard/dashboard.py`
   - Add your Gmail credentials:
     ```python
     SMTP_EMAIL = "your-email@gmail.com"
     SMTP_PASSWORD = "your-app-password"  # Use Gmail app password for security
     ```

## Running the System

### Option 1: Automated Startup (Windows)
```bash
run.bat
```
This launches all three components in separate terminal windows.

### Option 2: Manual Startup

**Terminal 1 - Backend API:**
```bash
cd backend
python app.py
```
Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 5500
```
Frontend accessible at `http://localhost:5500`

**Terminal 3 - Dashboard:**
```bash
cd dashboard
python dashboard.py
```
Opens the admin dashboard GUI window.

## Usage

### For Customers
1. Open `http://localhost:5500` in your browser
2. Enter username, email, and support message
3. Click "Submit Ticket"
4. Your ticket ID will appear on screen

### For Support Staff
1. Dashboard opens automatically (if using run.bat)
2. View ticket list on the left side
3. Click a ticket to view details
4. Use dropdown to change status (open/in-progress/closed)
5. Type message in text box and click "Send Update" to respond
6. Updates are sent via email to customer

## API Examples

### Create a Support Ticket
```bash
curl -X POST http://localhost:8000/support/request \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"John\", \"email\": \"john@example.com\", \"message\": \"Can't login\"}"
```

### Get All Tickets (Admin)
```bash
curl http://localhost:8000/admin/tickets
```

### Update Ticket Status
```bash
curl -X POST http://localhost:8000/admin/status \
  -H "Content-Type: application/json" \
  -d "{\"ticket_id\": 1, \"status\": \"in-progress\"}"
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CUSTOMER BROWSER                      │
│              (HTML/JS Frontend - Port 5500)            │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Requests
                     ↓
┌─────────────────────────────────────────────────────────┐
│              FLASK REST API (Port 8000)                 │
│              (Backend - app.py)                         │
└────────────────────┬────────────────────────────────────┘
                     │ SQLite Queries
                     ↓
┌─────────────────────────────────────────────────────────┐
│           SQLITE DATABASE (support.db)                  │
│          (Tickets & Updates Tables)                    │
└─────────────────────────────────────────────────────────┘
                     ↑
                     │ REST Calls
                     │
┌─────────────────────────────────────────────────────────┐
│        SUPPORT DASHBOARD GUI (Tkinter)                  │
│           (Admin Interface)                             │
│     - View & manage tickets                             │
│     - Send email updates                                │
└─────────────────────────────────────────────────────────┘
```

## File Details

- **app.py** - Flask backend with CORS support, handles all ticket operations
- **database.py** - SQLite abstraction layer for database operations
- **dashboard.py** - Tkinter GUI application for support staff administration
- **app.js** - Frontend JavaScript for form submission and API communication
- **index.html** - Customer-facing web form
- **style.css** - UI styling

## Troubleshooting

**Dashboard won't send emails:**
- Ensure SMTP credentials are configured in `dashboard/dashboard.py`
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password
- Check that less secure apps are enabled (if not using App Password)

**Frontend can't connect to backend:**
- Verify backend is running on port 8000
- Check that Flask is installed: `pip install flask flask-cors`
- CORS is enabled, so cross-origin requests should work

**Database errors:**
- The database file `support.db` is created automatically on first run
- If corrupted, delete it and restart the backend

## Future Enhancements

- User authentication & multi-admin support
- Ticket priority levels
- File attachments
- Email notifications to customers
- Search/filter functionality
- Export reports

## License

This project is provided as-is for educational and business use.
