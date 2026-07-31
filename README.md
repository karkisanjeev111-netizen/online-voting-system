# CivicVote — Secure Online Voting System

A full-stack online voting web application built with **Flask**, **Jinja2**,
**SQLAlchemy**, and vanilla **HTML/CSS/JavaScript**.

## Features

### Four CRUD resourcess
| Resource       | Create                          | Read                                   | Update                              | Delete                          |
|----------------|----------------------------------|-----------------------------------------|--------------------------------------|-----------------------------------|
| **Elections**  | Admin creates an election       | Anyone logged in can list/view          | Admin edits title/dates/description | Admin deletes (cascades)         |
| **Candidates** | Admin adds a candidate           | Listed on election page / detail page   | Admin edits name/bio                | Admin removes                    |
| **Votes**      | Voter casts one vote per election| Voter views "My Votes"                  | Voter changes vote (while active)   | Voter retracts vote (while active)|
| **Users**      | Public self-registration         | Admin lists all users                   | Admin changes role/active status    | Admin deletes account            |

### User & session management
- Registration with server-side validation (unique username/email, password
  complexity policy).
- Login via **Flask-Login** sessions; "remember me" support.
- Per-user profile page: update email, change password (requires current
  password), delete own account.
- Role-based access control: `voter` vs `admin`.
- Account lockout after repeated failed logins; generic error messages that
  don't reveal whether a username exists.

## Security architecture & design principles

This project deliberately layers multiple, independent defenses (defense in
depth) rather than relying on any single control:

1. **Authentication & session security**
   - Passwords hashed with Werkzeug's PBKDF2-SHA256 (salted, one-way).
   - Sessions are signed/tamper-proof (Flask's `SECRET_KEY`), `HttpOnly`,
     `SameSite=Lax`, with a 30-minute idle timeout.
   - `login_manager.session_protection = "strong"` ties the session to the
     client fingerprint, invalidating it if hijacked from another device.
   - Login rate-limited (Flask-Limiter) and accounts lock temporarily after
     5 failed attempts.

2. **Authorization (RBAC)**
   - Every mutating route is protected by `@login_required` and, for
     admin-only actions, a custom `@admin_required` decorator (403 for
     non-admins, 401 for anonymous users).
   - Ownership checks on votes: a user may only edit/delete **their own**
     vote — enforced at the route level, not just hidden in the UI.

3. **CSRF protection**
   - Every state-changing form (Flask-WTF) includes a CSRF token; the
     server rejects any POST without a valid, session-bound token.

4. **Injection & XSS prevention**
   - All database access goes through the SQLAlchemy ORM with bound
     parameters — no raw/string-built SQL anywhere, which eliminates SQL
     injection as an attack surface.
   - Jinja2 autoescapes all template output by default, neutralizing
     reflected/stored XSS from user-supplied text (candidate bios,
     election descriptions, usernames, etc.).
   - A `Content-Security-Policy` header further restricts script sources.

5. **Business-logic integrity (the "one voter, one vote" guarantee)**
   - Enforced **twice**: once in application logic (checked before
     insert) and once with a **database-level unique constraint** on
     `(election_id, user_id)`. Even a race condition or a direct API call
     that bypasses the UI cannot produce two votes for the same user in
     the same election — the DB will reject the second insert.
   - Voting is only accepted while an election's computed `status` is
     `active` (server-computed from `start_date`/`end_date`, not
     trusted from the client).

6. **Secure defaults & fail-safe design**
   - `SECRET_KEY` and admin credentials are read from environment
     variables, never hardcoded; a random key/password is generated as a
     fallback for local demos only, with a clear console warning.
   - Security headers (`X-Content-Type-Options`, `X-Frame-Options`,
     `Referrer-Policy`, CSP) are set on every response.
   - Open-redirect protection on the post-login `next` parameter (only
     relative, in-app paths are honored).
   - Not even admins can edit another user's cast vote (ballot secrecy/
     integrity is preserved even against a compromised admin account).

## Tech stack
- **Backend:** Flask (application factory + Blueprints)
- **Templating:** Jinja2 (template inheritance, macros for form rendering)
- **Database:** MySQL (via PyMySQL), managed through the SQLAlchemy ORM —
  SQLite supported as a fallback for quick local demos
- **Forms/validation:** Flask-WTF / WTForms
- **Frontend:** hand-written HTML/CSS/JS (no framework) — responsive nav,
  flash messages, confirm dialogs, live result bars

## Project structure
voting_system/
├── app.py # App factory, extension wiring, security headers
├── config.py # Centralized, environment-driven configuration
├── extensions.py # Flask extension singletons
├── models.py # User, Election, Candidate, Vote (SQLAlchemy)
├── forms.py # WTForms with validators (incl. password policy)
├── decorators.py # @admin_required RBAC decorator
├── blueprints/
│ ├── main.py # Home + dashboard
│ ├── auth.py # Register / login / logout / profile
│ ├── elections.py # Elections CRUD + results
│ ├── candidates.py # Candidates CRUD
│ ├── votes.py # Votes CRUD (cast / change / retract)
│ └── admin.py # User management CRUD (admin only)
├── templates/ # Jinja2 templates (base layout + per-feature)
├── static/css/style.css # Design system (CSS variables, responsive)
├── static/js/main.js # Nav toggle, confirm dialogs, flash auto-dismiss
└── requirements.txt
## Setup & running locally

### 1. Set up MySQL
This project is built and tested against MySQL. Create the database and a
dedicated application user (run inside the `mysql` client, e.g. `mysql -u root -p`):

```sql
CREATE DATABASE civicvote CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'civicvote_app'@'localhost' IDENTIFIED BY 'choose-a-password';
GRANT ALL PRIVILEGES ON civicvote.* TO 'civicvote_app'@'localhost';
FLUSH PRIVILEGES;
```

(Don't have MySQL installed locally? Tools like XAMPP, MAMP, or Docker's
`mysql:8` image all work — just point `DATABASE_URL` at whichever host/port
you end up with.)

### 2. Install dependencies and configure

```bash
cd voting_system
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY` — a real random value (or generate one: `python3 -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL` — `mysql+pymysql://civicvote_app:choose-a-password@localhost/civicvote` (matching what you created in step 1)
- `ADMIN_USERNAME` / `ADMIN_EMAIL` / `ADMIN_PASSWORD` — your default admin login

### 3. Run it

```bash
python3 app.py
```

The first run creates all tables in MySQL and bootstraps a default admin
account using the environment variables above (or prints a generated
password if you don't set `ADMIN_PASSWORD`).

Then open **http://127.0.0.1:5000**.

> **No MySQL available?** Set `DATABASE_URL=sqlite:///voting.db` in `.env`
> instead for a quick local demo — the app runs identically against SQLite
> since all queries go through the SQLAlchemy ORM. The graded/deployed
> version should use MySQL as above.

### Typical workflow
1. Log in as `admin` → **Dashboard** → **+ New Election** (set start/end
   date-time).
2. Open the election → **+ Add Candidate** (repeat for each candidate).
3. Register a normal voter account (or several) and log in as them.
4. Once the election's start time has passed, voters see **Cast Your
   Vote** on the election page or dashboard.
5. After the end time passes, anyone can view **Results** with live vote
   bars and the winner highlighted.

## Testing

CivicVote has an automated test suite of **40 passing tests** covering
authentication, role-based access control, full CRUD on all four resources,
and security mechanisms (CSRF, password hashing, session cookies).

```bash
pip install -r requirements.txt   # includes pytest
python -m pytest tests/ -v
```

See [`TESTING.md`](TESTING.md) for full details, including manual
verification steps run directly against a live MySQL database. The raw test
run output is saved in [`tests/test_run_log.txt`](tests/test_run_log.txt).

## Project links

- **Author:** Sanjeev Karki (Student ID: 250202)
- **GitHub repository:** https://github.com/karkisanjeev111-netizen/online-voting-system
- **Demonstration video (YouTube, Unlisted):** `[add your video URL here once recorded and uploaded]`

## Troubleshooting

**`ModuleNotFoundError: No module named 'pymysql'` or the app can't reach MySQL:**
The app is fail-safe about this — if PyMySQL isn't installed, or a MySQL
server isn't reachable at the configured `DATABASE_URL`, it automatically
falls back to a local SQLite database and prints a clear warning explaining
why, instead of crashing. You'll see something like:

