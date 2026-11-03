class Device:
    def __init__(self, name):
        self.name = name
        self.online = True
        self.infected = False
        self.files_locked = False

    def infect(self):
        self.infected = True

    def lock_files(self):
        self.files_locked = True

    def disconnect(self):
        self.online = False

    def recover(self):
        self.online = True
        self.infected = False
        self.files_locked = False


class Connection:
    def __init__(self, name, device_a, device_b):
        self.name = name
        self.device_a = device_a
        self.device_b = device_b
        self.intercepted = False

    @property
    def online(self):
        return self.device_a.online and self.device_b.online

    def intercept(self):
        self.intercepted = True

    def secure(self):
        self.intercepted = False
