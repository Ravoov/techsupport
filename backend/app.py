from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from database import (
    init_db,
    create_ticket,
    get_email,
    add_update,
    list_tickets,
    get_ticket_with_updates,
    update_status
)

app = Flask(__name__)
CORS(app)

init_db()

@app.route("/support/request", methods=["POST"])
def support_request():
    data = request.get_json()
    email = data["email"]
    username = data["username"]
    message = data["message"]

    ticket_id = create_ticket(email, username, message)

    # Dashboard handles email sending locally
    return jsonify({"ticket_id": ticket_id, "status": "received"})


@app.route("/admin/tickets", methods=["GET"])
def admin_tickets():
    rows = list_tickets()
    return jsonify([
        {"id": r[0], "username": r[1], "message": r[2], "status": r[3]}
        for r in rows
    ])


@app.route("/admin/ticket/<int:ticket_id>", methods=["GET"])
def admin_ticket(ticket_id):
    ticket, updates = get_ticket_with_updates(ticket_id)
    if not ticket:
        return jsonify({"error": "not found"}), 404

    return jsonify({
        "id": ticket_id,
        "username": ticket[0],
        "message": ticket[1],
        "status": ticket[2],
        "updates": [{"text": u[0], "timestamp": u[1]} for u in updates]
    })


@app.route("/admin/update", methods=["POST"])
def admin_update():
    data = request.get_json()
    ticket_id = data["ticket_id"]
    text = data["message"]

    ts = datetime.now().isoformat()
    add_update(ticket_id, text, ts)

    return jsonify({"status": "sent"})


@app.route("/admin/status", methods=["POST"])
def admin_status():
    data = request.get_json()
    ticket_id = data["ticket_id"]
    new_status = data["status"]

    update_status(ticket_id, new_status)

    return jsonify({"status": "updated"})


@app.route("/admin/email/<int:ticket_id>", methods=["GET"])
def admin_email(ticket_id):
    email = get_email(ticket_id)
    return jsonify({"email": email})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)