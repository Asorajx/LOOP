class Victim:
    def __init__(self, name):
        self.name = name

    def isolate(self, device):
        device.disconnect()

    def recover(self, device):
        device.recover()

    def secure(self, connection):
        connection.secure()
