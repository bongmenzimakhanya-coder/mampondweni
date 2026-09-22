# Mampondweni Miracle Centre — Bible Lesson Schedule

A small website with two sides:

- **Public schedule** (`/`) — anyone with the link can view it. No login.
  Shows upcoming lessons (soonest first, with the next one marked), and
  past lessons tucked under a "Past lessons" toggle.
- **Admin area** (`/admin`) — one admin login. Add, edit, and delete
  lessons: **Date, Assigned member, Book, Chapter, Contact.**

Built with Flask + a database (SQLite by default — see "Data storage"
below), ready to deploy on [Railway](https://railway.app).

---

## Running it locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`. The default admin login is:

```
username: admin
password: changeme
```

The app prints a warning on startup reminding you these are defaults —
change them before this is public (see below).

A `data/mampondweni.db` SQLite file is created automatically the first
time you run it. Delete it any time to start fresh (you'll lose all
logged lessons).

---

## Deploying to Railway

1. **Push this project to a GitHub repo** (or use the Railway CLI to
   deploy the folder directly — `railway up` from inside this folder
   works too, no GitHub required).

2. **Create a new Railway project** from that repo (or that `railway up`
   deploy). Railway will detect the `Procfile` and `requirements.txt`
   automatically — no extra configuration needed to get it running.

3. **Set these environment variables** in Railway (Project → Variables).
   All three are required — without them the site runs on insecure
   defaults:

   | Variable | What to set it to |
   |---|---|
   | `SECRET_KEY` | A long random string, e.g. run `python -c "import secrets; print(secrets.token_hex(32))"` locally and paste the output |
   | `ADMIN_USERNAME` | Whatever username you want to log in with |
   | `ADMIN_PASSWORD` | A real password — not `changeme` |

4. **Add a Volume so your data survives redeploys.** Railway's
   filesystem is wiped on every redeploy unless you attach a Volume:
   - In your Railway service, go to **Settings → Volumes → New Volume**.
   - Set the **mount path** to `/data`.
   - Add one more environment variable: `DATA_DIR` = `/data`.

   Without this step, every time you redeploy (e.g. pushing a code
   change), the lesson schedule will reset to empty. With it, the
   SQLite file lives on the Volume and survives redeploys indefinitely.

5. **Deploy.** Railway gives you a public URL (something like
   `mampondweni-production.up.railway.app`) — that's the link you share
   for the public schedule. Add `/admin` to the end of it to log in.

That's it — no separate database service to provision. If you'd rather
use Railway's Postgres plugin instead of the SQLite + Volume approach,
add a Postgres service in Railway and set `DATABASE_URL` to the
connection string it gives you (this overrides `DATA_DIR`/SQLite
automatically — no code changes needed).

---

## Data storage

By default, everything is stored in one SQLite file — no separate
database to install or maintain, same idea as a single spreadsheet, just
managed through the admin screens instead of opened directly.

- **Locally:** `data/mampondweni.db`, next to `app.py`.
- **On Railway:** wherever `DATA_DIR` points (see step 4 above) — `/data`
  on the attached Volume, so it persists across redeploys.
- **Optional:** set `DATABASE_URL` to a Postgres connection string (e.g.
  from Railway's Postgres plugin) to use that instead — no code changes
  needed, it's checked before the SQLite default.

---

## Changing the admin password later

Just update the `ADMIN_PASSWORD` (and `ADMIN_USERNAME`, if you want)
environment variable in Railway and redeploy/restart the service —
nothing else to change.

## Notes

- The public schedule (`/`) never requires login — that's by design, so
  the congregation can check it without an account.
- Everything under `/admin` requires login.
- Session cookies are signed with `SECRET_KEY`. If you don't set it, a
  random one is generated each time the app starts, which logs
  everyone out on every restart/redeploy — set it once and forget it.
