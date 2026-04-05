import tkinter as tk
from tkinter import messagebox, ttk
import requests
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_URL = "http://127.0.0.1:8000"

# --- SMTP CONFIG (loaded from .env) ---
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

def send_local_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email failed: {e}")

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Support Dashboard Pro")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f2f5")
        self.tickets = []  # Initialize empty ticket list
        self.current_ticket_id = None

        # Define Styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f2f5")
        self.style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Action.TButton", font=("Segoe UI", 9, "bold"))

        # --- MAIN LAYOUT ---
        # Left Panel (Ticket List)
        left_panel = ttk.Frame(root, padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left_panel, text="All Tickets", style="Header.TLabel").pack(pady=(0, 10))
        
        self.ticket_list = tk.Listbox(
            left_panel, width=45, font=("Segoe UI", 10), 
            borderwidth=0, highlightthickness=1, highlightbackground="#ccc",
            selectbackground="#0078d4"
        )
        self.ticket_list.pack(fill=tk.BOTH, expand=True)
        self.ticket_list.bind("<<ListboxSelect>>", self.on_select)

        # Right Panel (Details)
        self.right_panel = ttk.Frame(root, padding="20")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Header Details
        ttk.Label(self.right_panel, text="Ticket Details", style="Header.TLabel").pack(anchor="w")
        
        self.details = tk.Text(
            self.right_panel, height=12, font=("Segoe UI", 10),
            bg="white", relief="flat", padx=10, pady=10,
            highlightthickness=1, highlightbackground="#ddd",
            state=tk.DISABLED # Start disabled until a ticket is picked
        )
        self.details.pack(fill=tk.BOTH, expand=True, pady=10)

        # Status & Controls Frame
        control_frame = ttk.Frame(self.right_panel)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Label(control_frame, text="Update Status:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar()
        self.status_menu = ttk.Combobox(control_frame, textvariable=self.status_var, values=["open", "in-progress", "closed"])
        self.status_menu.pack(side=tk.LEFT, padx=10)

        save_status_btn = ttk.Button(control_frame, text="Save Status", command=self.save_status)
        save_status_btn.pack(side=tk.LEFT)

        # Update Section
        ttk.Label(self.right_panel, text="Send Response to User:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15, 5))
        
        self.update_entry = tk.Text(
            self.right_panel, height=5, font=("Segoe UI", 10),
            bg="white", relief="flat", padx=10, pady=10,
            highlightthickness=1, highlightbackground="#ddd"
        )
        self.update_entry.pack(fill=tk.X, pady=5)

        send_btn = ttk.Button(self.right_panel, text="Send Update & Email", command=self.send_update, style="Action.TButton")
        send_btn.pack(anchor="e", pady=5)

        self.load_tickets()

    def load_tickets(self):
        try:
            self.ticket_list.delete(0, tk.END)
            res = requests.get(f"{BASE_URL}/admin/tickets")
            self.tickets = res.json()
            
            for t in self.tickets:
                status = t.get('status', 'open').lower()
                icon = "🟢" if status == 'open' else "🟡" if status == 'in-progress' else "🔴"
                
                display_text = f" {icon} Ticket #{t['id']} | {status.upper()} | {t['username']}"
                self.ticket_list.insert(tk.END, display_text)
                
                # Apply color coding to the list rows
                idx = self.ticket_list.size() - 1
                if status == 'closed':
                    self.ticket_list.itemconfig(idx, {'fg': 'gray'})
                elif status == 'in-progress':
                    self.ticket_list.itemconfig(idx, {'fg': '#b08d05'}) 
                    
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to backend: {e}")

    def on_select(self, event):
        selection = self.ticket_list.curselection()
        if not selection: return
        
        index = selection[0]
        ticket_id = self.tickets[index]["id"]
        self.load_ticket_details(ticket_id)

    def load_ticket_details(self, ticket_id):
        try:
            res = requests.get(f"{BASE_URL}/admin/ticket/{ticket_id}")
            data = res.json()
            self.current_ticket_id = ticket_id

            self.details.config(state=tk.NORMAL)
            self.details.delete("1.0", tk.END)
            
            self.details.insert(tk.END, f"USER: {data['username']}\n")
            self.details.insert(tk.END, f"EMAIL: {data.get('email', 'N/A')}\n")
            self.details.insert(tk.END, f"STATUS: {data['status'].upper()}\n")
            self.details.insert(tk.END, "-"*40 + "\n")
            self.details.insert(tk.END, f"MESSAGE:\n{data['message']}\n\n")
            self.details.insert(tk.END, "HISTORY:\n")

            for u in data.get("updates", []):
                self.details.insert(tk.END, f"[{u['timestamp']}] {u['text']}\n")
            
            self.status_var.set(data["status"])
            self.details.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ticket: {e}")

    def save_status(self):
        if not self.current_ticket_id: return
        new_status = self.status_var.get()
        requests.post(f"{BASE_URL}/admin/status", json={
            "ticket_id": self.current_ticket_id,
            "status": new_status
        })
        messagebox.showinfo("Success", "Status updated.")
        self.load_tickets() # Refresh list to update icons
        self.load_ticket_details(self.current_ticket_id)

    def send_update(self):
        if not self.current_ticket_id: return
        text = self.update_entry.get("1.0", tk.END).strip()
        if not text: return

        requests.post(f"{BASE_URL}/admin/update", json={
            "ticket_id": self.current_ticket_id,
            "message": text
        })

        try:
            email_res = requests.get(f"{BASE_URL}/admin/email/{self.current_ticket_id}")
            email = email_res.json()["email"]
            send_local_email(email, f"Update on ticket #{self.current_ticket_id}", text)
        except:
            print("Backend email lookup failed, but response was logged.")

        messagebox.showinfo("Sent", "Response logged and emailed.")
        self.update_entry.delete("1.0", tk.END)
        self.load_ticket_details(self.current_ticket_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardApp(root)
    root.mainloop()