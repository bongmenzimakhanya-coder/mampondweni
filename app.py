"""
Mampondweni Miracle Centre - Bible Lesson Schedule
----------------------------------------------------
Public: anyone with the link can view the schedule, read-only, no login.
Admin:  one admin account (ADMIN_USERNAME / ADMIN_PASSWORD, see
        config.py) can log in to add, edit, and delete lessons.

Run locally with:
    python app.py
Then open:
    http://localhost:5000

See README.md for deploying this to Railway.
"""

import hmac
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session

import config
from models import db, Lesson, OLD_TESTAMENT, NEW_TESTAMENT

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

with app.app_context():
    db.create_all()
    if config.USING_DEFAULT_CREDENTIALS:
        print("\n[WARNING] Using the default admin username/password (admin/changeme).")
        print("          Set ADMIN_USERNAME and ADMIN_PASSWORD before going live — see README.md.\n")
    if config.USING_DEFAULT_SECRET_KEY:
        print("[WARNING] Using the default SECRET_KEY — everyone gets logged out on every")
        print("          restart/redeploy until you set a real one. See README.md.\n")


# ---------- Auth helpers ----------

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def _check_credentials(username, password):
    # constant-time comparison so a login attempt can't be used to guess
    # the password one character at a time via response-time differences
    user_ok = hmac.compare_digest(username or "", config.ADMIN_USERNAME)
    pass_ok = hmac.compare_digest(password or "", config.ADMIN_PASSWORD)
    return user_ok and pass_ok


# ---------- Public: read-only schedule ----------

@app.route("/")
def schedule():
    today = datetime.now().date()
    all_lessons = Lesson.query.order_by(Lesson.date.asc()).all()
    upcoming = [l for l in all_lessons if l.date >= today]
    past = sorted([l for l in all_lessons if l.date < today], key=lambda l: l.date, reverse=True)
    next_id = upcoming[0].id if upcoming else None
    return render_template(
        "schedule.html",
        upcoming=upcoming,
        past=past,
        next_id=next_id,
        today=today,
    )


# ---------- Admin: auth ----------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if _check_credentials(username, password):
            session["is_admin"] = True
            flash("Logged in.", "success")
            return redirect(request.args.get("next") or url_for("admin_dashboard"))
        flash("Incorrect username or password.", "error")
        return redirect(url_for("admin_login", next=request.args.get("next")))

    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))
    return render_template("login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out.", "success")
    return redirect(url_for("schedule"))


# ---------- Admin: manage lessons ----------

@app.route("/admin")
@admin_required
def admin_dashboard():
    lessons = Lesson.query.order_by(Lesson.date.asc()).all()
    today = datetime.now().date()
    return render_template("admin_dashboard.html", lessons=lessons, today=today)


def _read_lesson_form():
    """Pulls + validates the shared add/edit form fields. Returns
    (data_dict, error_message) — error_message is None if everything's
    valid."""
    date_str = request.form.get("date", "").strip()
    assigned_member = request.form.get("assigned_member", "").strip()
    book = request.form.get("book", "").strip()
    chapter = request.form.get("chapter", "").strip()
    contact = request.form.get("contact", "").strip()

    if not date_str:
        return None, "Date is required."
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None, "That date couldn't be read — please use the date picker."

    if not assigned_member:
        return None, "Assigned member is required."
    if not book:
        return None, "Please choose a book."
    if book not in OLD_TESTAMENT and book not in NEW_TESTAMENT:
        return None, "Please choose a book from the list."
    if not chapter:
        return None, "Chapter is required."

    return {
        "date": date_obj,
        "assigned_member": assigned_member,
        "book": book,
        "chapter": chapter,
        "contact": contact,
    }, None


@app.route("/admin/add", methods=["GET", "POST"])
@admin_required
def add_lesson():
    if request.method == "POST":
        data, error = _read_lesson_form()
        if error:
            flash(error, "error")
            return redirect(url_for("add_lesson"))
        lesson = Lesson(**data)
        db.session.add(lesson)
        db.session.commit()
        flash(f"Lesson scheduled for {data['assigned_member']} on {data['date'].strftime('%d %b %Y')}.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "lesson_form.html",
        mode="add",
        lesson=None,
        old_testament=OLD_TESTAMENT,
        new_testament=NEW_TESTAMENT,
        today=datetime.now().strftime("%Y-%m-%d"),
    )


@app.route("/admin/edit/<int:lesson_id>", methods=["GET", "POST"])
@admin_required
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if request.method == "POST":
        data, error = _read_lesson_form()
        if error:
            flash(error, "error")
            return redirect(url_for("edit_lesson", lesson_id=lesson_id))
        lesson.date = data["date"]
        lesson.assigned_member = data["assigned_member"]
        lesson.book = data["book"]
        lesson.chapter = data["chapter"]
        lesson.contact = data["contact"]
        db.session.commit()
        flash("Lesson updated.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "lesson_form.html",
        mode="edit",
        lesson=lesson,
        old_testament=OLD_TESTAMENT,
        new_testament=NEW_TESTAMENT,
        today=datetime.now().strftime("%Y-%m-%d"),
    )


@app.route("/admin/delete/<int:lesson_id>", methods=["POST"])
@admin_required
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    db.session.delete(lesson)
    db.session.commit()
    flash("Lesson removed.", "success")
    return redirect(url_for("admin_dashboard"))


# ---------- Errors ----------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="That page doesn't exist."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500, message="Something went wrong on this end."), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
