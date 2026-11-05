"""Short terminal stories, code explanations and OOP concepts for the library scenario.

Each EXPLAIN entry matches a real method or code line.
Story = what has happened at this step. Code = what the Python line does.
Concept = a relevant OOP idea (only when helpful).
Lines that return True or False can use story_true/story_false and
code_true/code_false so the text matches the real result.

Placeholders: {target} is the chosen book, {member} and {library} are the
objects from build(). Each is replaced by the object's display name.
"""

ACTION_STORIES = {
    "borrow": "{member} tries to borrow {target}.",
    "return": "{member} tries to return {target}.",
    "renew": "{member} tries to renew the loan of {target}.",
    "check": "{member} asks whether {target} is available.",
}

ACTION_SUMMARIES = {
    "borrow": {
        "success": {
            "story": "{member} successfully borrows {target}. The other book isn't affected.",
            "concept": "relationships",
            "lesson": "{member} asked {library}, and {library} asked {target}. {target} now holds a "
                      "reference to {member} in its borrowed_by attribute.",
        },
        "failure": {
            "story": "{member} cannot borrow {target} because it is already borrowed.",
            "concept": "encapsulation",
            "lesson": "{target}'s own borrow() method checked whether it was available and refused, "
                      "so none of its attributes changed. The Book looks after its own loan details.",
        },
    },
    "return": {
        "success": {
            "story": "{member} returns {target}, and it is available again.",
            "concept": "encapsulation",
            "lesson": "{library} didn't change {target}'s attributes itself. It asked {target}, and "
                      "the Book's own return_book() method cleared the loan.",
        },
        "failure": {
            "story": "{member} cannot return {target} because {member} has not borrowed it.",
            "concept": "methods",
            "lesson": "return_book() checked borrowed_by first. {member} is not the borrower, so the "
                      "method returned False and nothing changed.",
        },
    },
    "renew": {
        "success": {
            "story": "{member} renews the loan of {target}. It has now been renewed once.",
            "concept": "attributes",
            "lesson": "Each Book keeps its own renewals count. {target}'s renew() method allows one "
                      "renewal per loan, and return_book() resets the count.",
        },
        "failure": [
            {
                "when": {"borrowed_by": None},
                "story": "{member} cannot renew {target} because it isn't borrowed.",
                "concept": "methods",
                "lesson": "renew() checked {target}'s borrowed_by attribute first. Nobody has borrowed "
                          "{target}, so the method returned False and nothing changed.",
            },
            {
                "story": "{member} cannot renew {target} because the loan has already been renewed once.",
                "concept": "methods",
                "lesson": "renew() checked {target}'s renewals attribute first. The loan was already "
                          "renewed once, so the method returned False and nothing changed.",
            },
        ],
    },
    "check": {
        "success": [
            {
                "when": {"available": True},
                "story": "{library} reports that {target} is available.",
                "concept": "properties",
                "lesson": "available looks like an attribute, but it's a property. Python works out "
                          "its value from borrowed_by each time it's read, so it is never out of date.",
            },
            {
                "story": "{library} reports that {target} is on loan.",
                "concept": "properties",
                "lesson": "available looks like an attribute, but it's a property. Python works out "
                          "its value from borrowed_by each time it's read, so it is never out of date.",
            },
        ],
    },
}

EXPLAIN = {
    "Member.borrow": {
        "call": {
            "story": "{member} starts a request to borrow {target}.",
            "code": "Start {member}'s borrow() method for {target}.",
        },
        "return library.lend(self, book)": {
            "story": "{member} asks {library} to lend {target}.",
            "code": "Call {library}'s lend() method with {member} (self) and {target}, then return its answer.",
            "concept": "relationships",
            "detail": "Objects can pass references to each other when they call methods. Here {member} "
                      "passes itself (self) and {target} to {library}.",
        },
    },
    "Library.lend": {
        "call": {
            "story": "{library} receives the request to lend {target}.",
            "code": "Start {library}'s lend() method for {target}.",
        },
        "return book.borrow(member)": {
            "story": "{library} asks {target} to handle the borrowing request.",
            "code": "Call {target}'s borrow() method with {member}, then return its answer.",
            "concept": "encapsulation",
            "detail": "{library} doesn't change {target}'s loan details itself. It asks {target}'s own "
                      "borrow() method to do it.",
        },
    },
    "Book.borrow": {
        "call": {
            "story": "{target} receives the borrowing request from {library}.",
            "code": "Start {target}'s borrow() method with {member}.",
        },
        "if not self.available:": {
            "story": "{target} checks whether it is available to borrow.",
            "code": "Read {target}'s available property. If {target} is not available, the request is rejected.",
        },
        "return False": {
            "story": "{target} is already borrowed, so it rejects the request.",
            "code": "Return False because {target} is already on loan.",
        },
        "self.borrowed_by = member": {
            "story": "{target} is now borrowed by {member}.",
            "code": "Store a reference to {member} in {target}'s borrowed_by attribute.",
            "concept": "relationships",
            "detail": "{target} now holds a reference to the {member} object, so it remembers who borrowed it.",
        },
        "self.renewals = 0": {
            "story": "{target} starts the new loan with zero renewals.",
            "code": "Set {target}'s renewals attribute to 0.",
        },
        "return True": {
            "story": "{target} confirms that the borrow request was successful.",
            "code": "Return True to show that {target} was successfully borrowed.",
        },
    },
    "Book.available": {
        "property": {
            "story": "{target} checks its current loan status.",
            "code": "Run {target}'s available property method to check if it is available.",
            "concept": "properties",
            "detail": "A property lets a method be read like an attribute. Reading {target}'s available "
                      "value runs this method to work out the answer. Nothing called available is "
                      "stored on {target}.",
        },
        "return self.borrowed_by is None": {
            "story": "{target} checks whether anyone has borrowed it.",
            "code": "Check whether {target} has a borrower, then return its availability.",
            "story_true": "{target} is not borrowed, so it is available.",
            "story_false": "{target} is already borrowed, so it is unavailable.",
            "code_true": "Since borrowed_by is None, return True to show {target} is available.",
            "code_false": "Since borrowed_by is not None, return False to show {target} is unavailable.",
        },
    },
    "Member.return_book": {
        "call": {
            "story": "{member} starts a request to return {target}.",
            "code": "Start {member}'s return_book() method for {target}.",
        },
        "return library.accept_return(self, book)": {
            "story": "{member} asks {library} to accept {target} back.",
            "code": "Call {library}'s accept_return() method with {member} (self) and {target}, "
                    "then return its answer.",
        },
    },
    "Library.accept_return": {
        "call": {
            "story": "{library} receives the return request for {target}.",
            "code": "Start {library}'s accept_return() method for {target}.",
        },
        "return book.return_book(member)": {
            "story": "{library} asks {target} to handle the return.",
            "code": "Call {target}'s return_book() method with {member}, then return its answer.",
        },
    },
    "Book.return_book": {
        "call": {
            "story": "{target} receives the return request from {library}.",
            "code": "Start {target}'s return_book() method with {member}.",
        },
        "if self.borrowed_by is not member:": {
            "story": "{target} checks whether {member} borrowed it.",
            "code": "Check whether {member} is {target}'s borrower. If not, the return is rejected.",
        },
        "return False": {
            "story": "{target} rejects the return because {member} is not its borrower.",
            "code": "Return False because {member} is not {target}'s borrower.",
        },
        "self.borrowed_by = None": {
            "story": "{target} no longer has a borrower.",
            "code": "Set borrowed_by to None. None means nobody has {target} on loan.",
            "concept": "encapsulation",
            "detail": "{target}'s own return_book() method changes its loan details. {library} never "
                      "changes them directly.",
        },
        "self.renewals = 0": {
            "story": "{target} resets its renewal count.",
            "code": "Set {target}'s renewals attribute back to 0 because the loan has ended.",
        },
        "return True": {
            "story": "{target} confirms that the return was successful.",
            "code": "Return True to confirm the return succeeded.",
        },
    },
    "Member.renew": {
        "call": {
            "story": "{member} starts a request to renew {target}.",
            "code": "Start {member}'s renew() method for {target}.",
        },
        "return library.renew_loan(self, book)": {
            "story": "{member} asks {library} to renew {target}.",
            "code": "Call {library}'s renew_loan() method with {member} (self) and {target}, "
                    "then return its answer.",
        },
    },
    "Library.renew_loan": {
        "call": {
            "story": "{library} receives the renewal request for {target}.",
            "code": "Start {library}'s renew_loan() method for {target}.",
        },
        "return book.renew(member)": {
            "story": "{library} asks {target} to handle the renewal.",
            "code": "Call {target}'s renew() method with {member}, then return its answer.",
        },
    },
    "Book.renew": {
        "call": {
            "story": "{target} receives the renewal request from {library}.",
            "code": "Start {target}'s renew() method with {member}.",
        },
        "if self.borrowed_by is not member or self.renewals >= 1:": {
            "story": "{target} checks whether {member} can renew its loan.",
            "code": "Check if {member} is not the borrower, or the loan has already been renewed once. "
                    "If either is true, the renewal is rejected.",
        },
        "return False": {
            "story": "{target} rejects the renewal.",
            "code": "Return False because {member} isn't the borrower, or the loan was already renewed once.",
        },
        "self.renewals += 1": {
            "story": "{target} adds one renewal to its loan.",
            "code": "Increase {target}'s renewals attribute by 1.",
            "concept": "attributes",
            "detail": "Each Book object keeps its own renewals count. Renewing {target} does not change "
                      "the other book.",
        },
        "return True": {
            "story": "{target} confirms that the renewal was successful.",
            "code": "Return True to confirm the renewal succeeded.",
        },
    },
    "Member.check": {
        "call": {
            "story": "{member} wants to know if {target} is available.",
            "code": "Start {member}'s check() method for {target}.",
        },
        "return library.check(book)": {
            "story": "{member} asks {library} about {target}.",
            "code": "Call {library}'s check() method with {target}, then return its answer.",
        },
    },
    "Library.check": {
        "call": {
            "story": "{library} receives {member}'s question about {target}.",
            "code": "Start {library}'s check() method for {target}.",
        },
        "if book.available:": {
            "story": "{library} checks whether {target} is available.",
            "code": "Read {target}'s available property to decide which answer to give.",
        },
        'return "Available"': {
            "story": "{library} reports that {target} is available.",
            "code": 'Return "Available" because nobody has borrowed {target}.',
        },
        'return "On loan"': {
            "story": "{library} reports that {target} is on loan.",
            "code": 'Return "On loan" because {target} has a borrower.',
        },
    },
}
