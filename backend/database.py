import sqlite3

DB_NAME = "support.db"  # If using Render Disk: "/var/data/support.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'open'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER,
            text TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


def create_ticket(email, username, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO tickets (email, username, message) VALUES (?, ?, ?)",
        (email, username, message)
    )
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def get_email(ticket_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT email FROM tickets WHERE id=?", (ticket_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def list_tickets():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, username, message, status FROM tickets")
    rows = c.fetchall()
    conn.close()
    return rows


def get_ticket_with_updates(ticket_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT username, message, status FROM tickets WHERE id=?", (ticket_id,))
    ticket = c.fetchone()

    c.execute("SELECT text, timestamp FROM updates WHERE ticket_id=?", (ticket_id,))
    updates = c.fetchall()

    conn.close()
    return ticket, updates


def add_update(ticket_id, text, timestamp):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO updates (ticket_id, text, timestamp) VALUES (?, ?, ?)",
        (ticket_id, text, timestamp)
    )
    conn.commit()
    conn.close()


def update_status(ticket_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE tickets SET status=? WHERE id=?", (new_status, ticket_id))
    conn.commit()
    conn.close()