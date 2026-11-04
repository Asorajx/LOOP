class Book:
    def __init__(self, name):
        self.name = name
        self.borrowed_by = None
        self.renewals = 0

    @property
    def available(self):
        return self.borrowed_by is None

    def borrow(self, member):
        if not self.available:
            return False
        self.borrowed_by = member
        self.renewals = 0
        return True

    def return_book(self, member):
        if self.borrowed_by is not member:
            return False
        self.borrowed_by = None
        self.renewals = 0
        return True

    def renew(self, member):
        if self.borrowed_by is not member or self.renewals >= 1:
            return False
        self.renewals += 1
        return True
