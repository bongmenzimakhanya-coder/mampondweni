"""
models.py
---------
The one table this app needs: a scheduled bible lesson. Kept deliberately
small — date, assigned member, book, chapter, contact — matching exactly
what was asked for.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    assigned_member = db.Column(db.String(120), nullable=False)
    book = db.Column(db.String(40), nullable=False)
    # String, not int: chapters are often given as a range or a
    # chapter:verse reference (e.g. "3", "3-5", "3:1-10").
    chapter = db.Column(db.String(40), nullable=False)
    contact = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "assigned_member": self.assigned_member,
            "book": self.book,
            "chapter": self.chapter,
            "contact": self.contact,
        }


# The 66 books, in canonical order, grouped for the <optgroup> dropdown
# on the lesson form — avoids typos and keeps the schedule consistent.
OLD_TESTAMENT = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel",
    "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
    "Haggai", "Zechariah", "Malachi",
]

NEW_TESTAMENT = [
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
    "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus",
    "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John",
    "2 John", "3 John", "Jude", "Revelation",
]

ALL_BOOKS = OLD_TESTAMENT + NEW_TESTAMENT
