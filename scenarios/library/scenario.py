"""Library scenario: a member borrows, returns and renews books through a library."""

from engine.scenario_manager import TARGET

from . import story
from .books import Book
from .library import Library
from .members import Member

TITLE = "Library"
ORDER = 2

PANELS = [
    ("Member", [Member]),
    ("Library", [Library, Book]),
]

# Attributes shown as small status icons. An icon lights up when the value differs
# from "normal". "icon" names one of the icons in web/js/icons.js.
STATUS = {
    "available": {"normal": True, "label": "On loan", "icon": "book", "tone": "warning",
                  "about": "Borrowed, so nobody else can take it until it's returned."},
}

BOOKS = ["BOOK001", "BOOK002"]

ACTIONS = [
    {"id": "borrow", "method": "Member.borrow", "targets": BOOKS,
     "call": ("member", "borrow", "library", TARGET)},
    {"id": "return", "method": "Member.return_book", "targets": BOOKS,
     "call": ("member", "return_book", "library", TARGET)},
    {"id": "renew", "method": "Member.renew", "targets": BOOKS,
     "call": ("member", "renew", "library", TARGET)},
    {"id": "check", "method": "Member.check", "targets": BOOKS,
     "call": ("member", "check", "library", TARGET)},
]


def build():
    return {
        "member": Member("Member A"),
        "library": Library("City Library"),
        "BOOK001": Book("Book A"),
        "BOOK002": Book("Book B"),
    }
