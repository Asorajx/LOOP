class Member:
    def __init__(self, name):
        self.name = name

    def borrow(self, library, book):
        return library.lend(self, book)

    def return_book(self, library, book):
        return library.accept_return(self, book)

    def renew(self, library, book):
        return library.renew_loan(self, book)

    def check(self, library, book):
        return library.check(book)
