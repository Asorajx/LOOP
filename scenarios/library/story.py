"""Storyboard, code explanations and OOP concepts for the library scenario.

Same format as scenarios/cybersecurity/story.py: EXPLAIN is keyed by method, then by
"call", "super", "property" or the exact text of a line in that method.
Tests check that every key matches the real source.
"""

ACTION_STORIES = {
    "borrow": "Member tries to borrow {target}.",
    "return": "Member tries to return {target}.",
    "renew": "Member tries to renew the loan of {target}.",
    "check": "Member asks whether {target} is available.",
}

# Shown when an action finishes: the result, and the one idea to remember.
ACTION_SUMMARIES = {
    "borrow": {
        "story": "Member has borrowed {target}. The other book isn't affected.",
        "concept": "relationships",
        "lesson": "Member asked Library, and Library asked the Book. The Book now holds a reference to the Member who borrowed it.",
    },
    "return": {
        "story": "{target} is returned and available again.",
        "concept": "encapsulation",
        "lesson": "Library didn't change the Book's attributes itself. It asked the Book, and the Book's own return_book() cleared its loan.",
    },
    "renew": {
        "story": "The loan of {target} is renewed.",
        "concept": "attributes",
        "lesson": "Each Book keeps its own renewals count, and its renew() method allows one renewal per loan.",
    },
    "check": {
        "story": "{target}: {result}.",
        "concept": "attributes",
        "lesson": "available looks like an attribute, but it's a property: Python works out the answer from borrowed_by each time it's read.",
    },
}

# Shown instead when an action's method returns False.
FALSE_SUMMARY = {
    "story": "Nothing changed: the Book's rules don't allow that right now.",
    "concept": "methods",
    "lesson": "The Book's method checked its own state first and returned False, so no attribute was changed.",
}

EXPLAIN = {
    "Member.borrow": {
        "return library.lend(self, book)": {
            "code": "Member passes itself and the chosen book to Library.",
            "concept": "relationships",
            "detail": "Objects can pass references to each other when they call methods.",
        },
    },
    "Library.lend": {
        "return book.borrow(member)": {
            "code": "Library hands the decision to the Book itself.",
        },
    },
    "Library.check": {
        "if book.available:": {
            "code": "Reading available asks the Book whether anyone has borrowed it.",
        },
    },
    "Book.available": {
        "property": {
            "code": "available looks like an attribute, but it's a property: reading it runs this method.",
            "concept": "attributes",
            "detail": "A property gives a value worked out from the object's current state.",
        },
    },
    "Book.borrow": {
        "if not self.available:": {
            "code": "A book that's already on loan can't be borrowed again.",
        },
        "self.borrowed_by = member": {
            "story": "{target} is now on loan to Member.",
            "code": "The Book remembers which Member object borrowed it.",
            "concept": "relationships",
            "detail": "One object can keep a reference to another object as an attribute.",
        },
    },
    "Book.return_book": {
        "if self.borrowed_by is not member:": {
            "code": "Only the member who borrowed the book can return it.",
        },
        "self.borrowed_by = None": {
            "story": "{target} has no borrower now.",
            "code": "The Book clears its own borrower.",
            "concept": "encapsulation",
            "detail": "The Book's own method is responsible for changing its loan details.",
        },
    },
    "Book.renew": {
        "if self.borrowed_by is not member or self.renewals >= 1:": {
            "code": "Only the borrower can renew, and only once per loan.",
        },
        "self.renewals += 1": {
            "story": "The loan of {target} is renewed.",
            "code": "The Book counts how many times this loan was renewed.",
            "concept": "attributes",
            "detail": "Each Book object keeps its own renewals count.",
        },
    },
}
