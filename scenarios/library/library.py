class Library:
    def __init__(self, name):
        self.name = name

    def lend(self, member, book):
        return book.borrow(member)

    def accept_return(self, member, book):
        return book.return_book(member)

    def renew_loan(self, member, book):
        return book.renew(member)

    def check(self, book):
        if book.available:
            return "Available"
        return "On loan"
