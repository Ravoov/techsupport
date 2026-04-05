require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const initSqlJs = require('sql.js');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.PORT || 3000;
const DB_PATH = path.join(__dirname, 'db', 'support.db');

// Ensure db directory exists
const dbDir = path.join(__dirname, 'db');
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// ─── Gmail Transporter ───────────────────────────────────────────────────────
function createTransporter() {
  const user = process.env.GMAIL_USER;
  const pass = process.env.GMAIL_APP_PASSWORD;
  if (!user || !pass || user === 'your_gmail@gmail.com') return null;
  return nodemailer.createTransport({ service: 'gmail', auth: { user, pass } });
}

// ─── Database ─────────────────────────────────────────────────────────────────
let db;

async function initDB() {
  const SQL = await initSqlJs();
  if (fs.existsSync(DB_PATH)) {
    db = new SQL.Database(fs.readFileSync(DB_PATH));
  } else {
    db = new SQL.Database();
  }
  db.run(`
    CREATE TABLE IF NOT EXISTS tickets (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL,
      email TEXT NOT NULL,
      problem TEXT NOT NULL,
      status TEXT DEFAULT 'open',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  saveDB();
  console.log('Database ready.');
}

function saveDB() {
  fs.writeFileSync(DB_PATH, Buffer.from(db.export()));
}

// ─── API Routes ───────────────────────────────────────────────────────────────

// User submits a ticket
app.post('/api/tickets', (req, res) => {
  const { username, email, problem } = req.body;
  if (!username || !email || !problem)
    return res.status(400).json({ error: 'All fields are required.' });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
    return res.status(400).json({ error: 'Invalid email address.' });

  db.run('INSERT INTO tickets (username, email, problem) VALUES (?, ?, ?)', [username, email, problem]);
  saveDB();
  const id = db.exec('SELECT last_insert_rowid() as id')[0].values[0][0];
  res.json({ success: true, ticketId: id });
});

// Admin: get all tickets — email field EXCLUDED
app.get('/api/admin/tickets', (req, res) => {
  const result = db.exec(
    'SELECT id, username, problem, status, created_at, updated_at FROM tickets ORDER BY created_at DESC'
  );
  if (!result.length) return res.json([]);
  const cols = result[0].columns;
  res.json(result[0].values.map(row => Object.fromEntries(cols.map((c, i) => [c, row[i]]))));
});

// Admin: check Gmail config status
app.get('/api/admin/email-status', (req, res) => {
  const configured = !!(
    process.env.GMAIL_USER &&
    process.env.GMAIL_APP_PASSWORD &&
    process.env.GMAIL_USER !== 'your_gmail@gmail.com'
  );
  res.json({ configured, sender: configured ? process.env.GMAIL_USER : null });
});

// Admin: get mailto link for local email sending
app.get('/api/admin/tickets/:id/mailto', (req, res) => {
  const { solution } = req.query;
  if (!solution?.trim()) return res.status(400).json({ error: 'Solution text is required.' });

  const result = db.exec('SELECT username, email, problem FROM tickets WHERE id = ?', [req.params.id]);
  if (!result.length || !result[0].values.length)
    return res.status(404).json({ error: 'Ticket not found.' });

  const [username, email, problem] = result[0].values[0];
  const esc = s => encodeURIComponent(s);

  const subject = `Re: Your Support Ticket #${req.params.id}`;
  const body = `Hi ${username},

Thank you for reaching out.

Solution:
${solution}

---
Your original issue:
${problem}

Best regards,
Tech Support Team`;

  const mailtoUrl = `mailto:${encodeURIComponent(email)}?subject=${esc(subject)}&body=${esc(body)}`;

  // Auto-move to in_progress if still open
  const cur = db.exec('SELECT status FROM tickets WHERE id = ?', [req.params.id]);
  if (cur.length && cur[0].values[0][0] === 'open') {
    db.run('UPDATE tickets SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', ['in_progress', req.params.id]);
    saveDB();
  }

  res.json({ mailto: mailtoUrl, email: email });
});

// Admin: send email — server fetches email, admin browser never sees it
app.post('/api/admin/tickets/:id/send-email', async (req, res) => {
  const { solution } = req.body;
  if (!solution?.trim()) return res.status(400).json({ error: 'Solution text is required.' });

  const result = db.exec('SELECT username, email, problem FROM tickets WHERE id = ?', [req.params.id]);
  if (!result.length || !result[0].values.length)
    return res.status(404).json({ error: 'Ticket not found.' });

  const [username, email, problem] = result[0].values[0];

  const transporter = createTransporter();
  if (!transporter) {
    return res.status(503).json({
      error: 'Gmail not configured. Copy .env.example to .env and add your Gmail credentials.'
    });
  }

  const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  try {
    await transporter.sendMail({
      from: `"SupportDesk" <${process.env.GMAIL_USER}>`,
      to: email,
      subject: `Re: Your Support Ticket #${req.params.id}`,
      text: `Hi ${username},\n\nThank you for reaching out.\n\nSolution:\n${solution}\n\n---\nYour original issue:\n${problem}\n\nBest regards,\nTech Support Team`,
      html: `
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
          <div style="background:#7c6af5;padding:24px 32px;border-radius:8px 8px 0 0;">
            <h2 style="color:white;margin:0;">⚡ SupportDesk</h2>
          </div>
          <div style="background:white;padding:32px;border:1px solid #e5e7eb;border-top:none;border-radius:0 0 8px 8px;">
            <p>Hi <strong>${esc(username)}</strong>,</p>
            <p>Thank you for contacting support. Here is the response to your ticket <strong>#${req.params.id}</strong>:</p>
            <div style="background:#f0fdf4;border-left:4px solid #22c55e;padding:16px 20px;border-radius:4px;margin:20px 0;">
              <p style="margin:0;white-space:pre-wrap;">${esc(solution)}</p>
            </div>
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;"/>
            <p style="color:#9ca3af;font-size:0.85rem;"><strong>Your original issue:</strong></p>
            <p style="color:#9ca3af;font-size:0.85rem;white-space:pre-wrap;">${esc(problem)}</p>
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;"/>
            <p style="color:#9ca3af;font-size:0.78rem;">This email was sent by SupportDesk in response to ticket #${req.params.id}.</p>
          </div>
        </div>`
    });

    // Auto-move to in_progress if still open
    const cur = db.exec('SELECT status FROM tickets WHERE id = ?', [req.params.id]);
    if (cur.length && cur[0].values[0][0] === 'open') {
      db.run('UPDATE tickets SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', ['in_progress', req.params.id]);
      saveDB();
    }

    console.log(`Email sent for ticket #${req.params.id}`);
    res.json({ success: true });
  } catch (err) {
    console.error('Email error:', err.message);
    res.status(500).json({ error: 'Failed to send: ' + err.message });
  }
});

// Admin: update ticket status
app.patch('/api/admin/tickets/:id/status', (req, res) => {
  const { status } = req.body;
  if (!['open', 'in_progress', 'resolved'].includes(status))
    return res.status(400).json({ error: 'Invalid status.' });
  db.run('UPDATE tickets SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', [status, req.params.id]);
  saveDB();
  res.json({ success: true });
});

app.get('/', (req, res) => res.sendFile(path.join(__dirname, 'public', 'index.html')));
app.get('/admin', (req, res) => res.sendFile(path.join(__dirname, 'public', 'admin.html')));

// ─── Start ────────────────────────────────────────────────────────────────────
initDB().then(() => {
  app.listen(PORT, () => {
    const ok = !!(process.env.GMAIL_USER && process.env.GMAIL_APP_PASSWORD && process.env.GMAIL_USER !== 'your_gmail@gmail.com');
    console.log(`\nSupportDesk → http://localhost:${PORT}`);
    console.log(`  User form:  http://localhost:${PORT}/`);
    console.log(`  Dashboard:  http://localhost:${PORT}/admin`);
    console.log(ok ? `\n  Gmail: ${process.env.GMAIL_USER}` : `\n  Gmail not configured — copy .env.example to .env\n`);
  });
});
