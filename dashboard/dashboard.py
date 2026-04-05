import tkinter as tk
from tkinter import messagebox
import requests
from email.mime.text import MIMEText
import smtplib

BASE_URL = "http://127.0.0.1:8000"

SMTP_EMAIL = ""
SMTP_PASSWORD = ""
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_local_email(to_email, subject, body):
    """Send email locally from the dashboard (Render cannot send SMTP)."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()


class DashboardApp:
    def __init__(self, root):
        self.root = root
        root.title("Support Dashboard")

        # LEFT SIDE — Ticket List
        self.ticket_list = tk.Listbox(root, width=45)
        self.ticket_list.pack(side=tk.LEFT, fill=tk.Y)
        self.ticket_list.bind("<<ListboxSelect>>", self.on_select)

        # RIGHT SIDE — Details + Controls
        right = tk.Frame(root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Ticket details
        self.details = tk.Text(right, height=15)
        self.details.pack(fill=tk.BOTH, expand=True)

        # Status dropdown
        self.status_var = tk.StringVar()
        self.status_menu = tk.OptionMenu(right, self.status_var, "open", "in-progress", "closed")
        self.status_menu.pack(pady=5)

        save_status_btn = tk.Button(right, text="Save Status", command=self.save_status)
        save_status_btn.pack(pady=5)

        # Update message box
        self.update_entry = tk.Text(right, height=5)
        self.update_entry.pack(fill=tk.X)

        send_btn = tk.Button(right, text="Send Update", command=self.send_update)
        send_btn.pack(pady=5)

        # Load tickets on startup
        self.load_tickets()

    def load_tickets(self):
        """Load all tickets from backend."""
        self.ticket_list.delete(0, tk.END)
        res = requests.get(f"{BASE_URL}/admin/tickets")
        self.tickets = res.json()

        for t in self.tickets:
            self.ticket_list.insert(
                tk.END,
                f"#{t['id']} | {t['username']} | {t['status']}"
            )

    def on_select(self, event):
        """When a ticket is clicked."""
        if not self.ticket_list.curselection():
            return

        index = self.ticket_list.curselection()[0]
        ticket_id = self.tickets[index]["id"]
        self.load_ticket_details(ticket_id)

    def load_ticket_details(self, ticket_id):
        """Load full ticket details + updates."""
        res = requests.get(f"{BASE_URL}/admin/ticket/{ticket_id}")
        data = res.json()
        self.current_ticket_id = ticket_id

        self.details.delete("1.0", tk.END)
        self.details.insert(tk.END, f"Ticket #{ticket_id}\n")
        self.details.insert(tk.END, f"User: {data['username']}\n")
        self.details.insert(tk.END, f"Message: {data['message']}\n")
        self.details.insert(tk.END, f"Status: {data['status']}\n\nUpdates:\n")

        for u in data["updates"]:
            self.details.insert(tk.END, f"- {u['timestamp']}: {u['text']}\n")

        # Set dropdown to current status
        self.status_var.set(data["status"])

    def save_status(self):
        """Save updated ticket status."""
        new_status = self.status_var.get()

        requests.post(f"{BASE_URL}/admin/status", json={
            "ticket_id": self.current_ticket_id,
            "status": new_status
        })

        messagebox.showinfo("Updated", "Status updated successfully.")
        self.load_ticket_details(self.current_ticket_id)
        self.load_tickets()

    def send_update(self):
        """Send update + email."""
        text = self.update_entry.get("1.0", tk.END).strip()
        if not text:
            return

        # Save update to backend
        requests.post(f"{BASE_URL}/admin/update", json={
            "ticket_id": self.current_ticket_id,
            "message": text
        })

        # Fetch email for sending
        email = requests.get(
            f"{BASE_URL}/admin/email/{self.current_ticket_id}"
        ).json()["email"]

        # Send email locally
        send_local_email(email, f"Update on ticket #{self.current_ticket_id}", text)

        messagebox.showinfo("Sent", "Update sent and email delivered.")
        self.update_entry.delete("1.0", tk.END)
        self.load_ticket_details(self.current_ticket_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()
