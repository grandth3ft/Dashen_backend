# Dashen Surveys — Phase 1

Online survey platform where users complete surveys and earn money.

## Status: Phase 6 complete — MVP finished 🎉
- [x] Project structure
- [x] Backend setup (Flask app factory, config, extensions, blueprint skeletons)
- [x] Frontend setup (Vite + React 18 + Tailwind v3 + Router + Axios + Toasts)
- [x] Dependencies declared
- [x] Database models (User, Survey, Question, Option, CompletedSurvey, WithdrawalRequest)
- [x] JWT auth — register, login, get/update profile, bcrypt password hashing
- [x] Tables auto-create + default admin account auto-seeds on first boot
- [x] Landing page, Login, Register — fully wired to backend
- [x] Dashboard + Profile — live wallet/stat data from GET /profile, editable via PUT /profile
- [x] PublicLayout / DashboardLayout, Sidebar, Navbar, Footer, ProtectedRoute
- [x] 10 companies × 12 questions auto-seeded (mixed types: multiple_choice, yes_no, radio, text)
- [x] GET /surveys, GET /survey/:id, POST /survey/:id/submit, GET /wallet
- [x] Surveys list, Survey Details, Take Survey (progress bar, prev/next, completion celebration)
- [x] Wallet page with merged earnings/withdrawal activity feed
- [x] Withdrawal system (POST /withdraw, GET /withdrawals, min KSh 300 rule, pending-aware balance check)
- [x] Full admin API (users, surveys CRUD, completed surveys, withdrawal approve/reject, dashboard stats)
- [x] Admin Dashboard, Users, Surveys (with question builder), Completed Surveys, Withdrawals UI
- [x] Real 404 page, entrance animations, mobile-safe truncation, JWT identity-casting bug fixed

### Bugs found and fixed in the Phase 6 audit
1. `index.html` referenced `/favicon.svg` but `frontend/public/` never existed — added it, favicon now resolves.
2. `auth_routes.py` passed the raw JWT identity string into `User.query.get()` while every other route cast it to `int` first — made consistent.
3. Stale "Phase 2 onward" comment left in `app.py` after routes were fully implemented — removed.
4. Long survey titles could overflow the Take Survey header on narrow screens — added `truncate`.
5. Admin survey builder required manually typing "Yes, No" and a 5-point scale every time — now auto-suggested (only if the field is empty, so it never overwrites an admin's own input).

### Known limitations (by design, not oversights — flagged for future work)
- Editing an existing survey's questions replaces the whole question set rather than diffing individual questions.
- Withdrawal requests are checked against balance-minus-pending at request time, not database-locked — fine for an MVP's traffic level, but a production version handling concurrent requests from the same user should wrap this in a row-level lock or serializable transaction.
- `SECRET_KEY` / `JWT_SECRET_KEY` default to placeholder dev values and `app.run(debug=True)` is on — both must change before any real deployment.
- [ ] Survey APIs, survey-taking UI, wallet logic — **Phase 4**
- [ ] Withdrawals + admin dashboard — **Phase 5**
- [ ] Polish, animations, responsiveness pass — **Phase 6**

## Project structure

```
Dashen-Surveys/
  backend/
    routes/        # Flask blueprints (auth, survey, wallet, withdrawal, admin)
    models/        # SQLAlchemy models (added Phase 2)
    database/      # SQLite file lives here in dev
    utils/         # helpers (seed script, decorators, etc.)
    config.py      # env-driven configuration
    extensions.py  # db, bcrypt, jwt, cors instances
    app.py         # application factory / entry point
    requirements.txt
  frontend/
    src/
      components/  # reusable UI pieces (added Phase 3+)
      pages/        # route-level pages (placeholders for now)
      layouts/      # Navbar/Sidebar/Footer wrappers (added Phase 3)
      services/     # api.js — single Axios instance
      hooks/
      context/      # AuthContext
      assets/
    package.json
```

## Running locally

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```
API runs at `http://localhost:5000`.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
App runs at `http://localhost:5173`.

> Both installs require internet access to pip/npm registries — run them on your own machine.

## Auth endpoints (Phase 2)

| Method | Endpoint    | Auth required | Body / notes |
|--------|-------------|----------------|---------------|
| POST   | `/register` | No             | `full_name, email, phone, password` |
| POST   | `/login`    | No             | `email, password` → returns JWT + user |
| GET    | `/profile`  | Yes (Bearer)   | Returns user + wallet stats |
| PUT    | `/profile`  | Yes (Bearer)   | Any of `full_name, email, phone, password` |

**Default admin account** (auto-seeded on first backend boot):
- Email: `admin@dashensurveys.com`
- Password: `Admin@123`

Change these in `backend/utils/seed.py` before deploying anywhere real.

## Survey & wallet endpoints (Phase 4)

| Method | Endpoint                  | Auth | Notes |
|--------|----------------------------|------|-------|
| GET    | `/surveys`                 | Yes  | Active surveys + `completed_by_user` flag per current user |
| GET    | `/survey/:id`               | Yes  | Full survey with questions + options |
| POST   | `/survey/:id/submit`        | Yes  | Body: `{ answers: { questionId: answer } }`. Blocks double-completion, credits wallet |
| GET    | `/wallet`                   | Yes  | Balance + merged earnings/withdrawal activity feed |

## Withdrawal & admin endpoints (Phase 5)

| Method | Endpoint                       | Auth        | Notes |
|--------|--------------------------------|-------------|-------|
| POST   | `/withdraw`                    | User        | `{ amount, till_number, account_name }`. Min KSh 300, checked against balance minus pending requests |
| GET    | `/withdrawals`                 | User        | Current user's own withdrawal history |
| GET    | `/admin/dashboard`              | Admin       | Summary stats for the 5 dashboard cards |
| GET    | `/admin/users`                  | Admin       | All registered users + wallet stats |
| GET/POST | `/admin/surveys`               | Admin       | List all / create a survey (with question builder) |
| PUT/DELETE | `/admin/surveys/:id`          | Admin       | Update or delete a survey |
| GET    | `/admin/completed`               | Admin       | All completed surveys across all users |
| GET    | `/admin/withdrawals`             | Admin       | All withdrawal requests, optional `?status=pending` filter |
| PUT    | `/admin/withdrawals/:id`         | Admin       | `{ status: "approved" \| "rejected" }` — approval deducts from wallet |

## Future extensibility
The architecture was kept deliberately simple so these can be layered in without restructuring:
- **Daraja STK Push / M-Pesa B2C** — swap the manual withdrawal form for a real payment call; `WithdrawalRequest.status` already models the pending → approved/rejected flow Daraja callbacks would drive.
- **Email verification / password reset** — `auth_routes.py` is isolated; add token-based verification endpoints alongside `/register` and `/login`.
- **PostgreSQL** — change one line in `.env` (`DATABASE_URL`); `config.py` and all models are already database-agnostic SQLAlchemy.
- **Notifications, referrals, coupons, survey categories, admin analytics/charts, CSV/PDF export, Docker, deployment** — each is additive: new models + a new blueprint, without touching existing code.

## Update: Account Tiers, Upgrade Payments & Withdrawal Field Change

Added after the initial MVP was already live in production.

### New: Free / Basic / Premium / Expert tier system
Only Free tier's numbers and the three upgrade prices were specified directly — everything else was derived to make each upgrade clearly worthwhile. Single source of truth: `backend/config.py` → `TIER_CONFIG`.

| Tier | Upgrade Cost | Surveys/day | Reward/survey | Min. withdrawal |
|---|---|---|---|---|
| Free | KSh 0 (default) | 1 | KSh 40–50 | KSh 4,500 |
| Business Basic | KSh 400 | 3 | KSh 60–80 | KSh 2,000 |
| Business Premium | KSh 800 | 6 | KSh 90–110 | KSh 1,000 |
| Business Expert | KSh 1,600 | Unlimited | KSh 120–150 | KSh 300 |

Reward per completed survey is now a random amount within the user's tier range, credited regardless of which specific survey they take (previously it was fixed per survey). Daily survey limits are enforced server-side, not just in the UI.

### New: manual M-Pesa upgrade-payment flow
- User picks a paid tier on **Upgrade** → sees the platform Till Number (`775566` — replace with your real one in `config.py`) and amount → pays via M-Pesa outside the app → clicks **Confirm Payment**, creating a `pending` upgrade request.
- Admin reviews it on **Admin → Upgrade Requests**: clicks **Confirm Payment** after checking the M-Pesa statement (→ `payment_confirmed`), then **Approve** (grants the tier) or **Decline** (no changes).

### Changed: withdrawals now collect a phone number, not a till number
Users enter an **amount** and their **M-Pesa phone number** (validated as `07XXXXXXXX` / `01XXXXXXXX`) instead of a till number + account name. The minimum withdrawal amount is now tier-based instead of a flat KSh 300.

### Database migration (safe for the already-live database)
Since `db.create_all()` only creates *new* tables — it never alters an existing one — `backend/utils/migrate.py` runs an idempotent check on every boot:
1. Adds `users.tier` (default `'free'`) if missing.
2. Renames `withdrawal_requests.till_number` → `phone_number` if the old column is still there.
3. Relaxes the old `account_name` column to nullable (kept, not dropped — reversible, no data loss).

**To apply this to your live site:** just redeploy the backend on Render (push this code, or manually trigger a deploy). The migration runs automatically on startup, before the app starts serving requests. No frontend environment changes are needed, and no manual database commands are required.

### Known limitation to flag
Daily survey limits reset at **UTC midnight**, not East Africa Time (UTC+3) — a user's "new day" currently starts at 3:00 AM Nairobi time, not midnight. Fine for launch; worth fixing with a proper timezone-aware boundary if it causes confusion.

## Getting started
See the "Running locally" section above. Once both servers are running: register a normal account to try the survey/wallet/withdrawal flow, or log in as the seeded admin (`admin@dashensurveys.com` / `Admin@123`) to manage surveys, users, and withdrawals.
# Dashen_backend
