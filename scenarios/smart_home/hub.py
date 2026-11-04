class HomeHub:
    def __init__(self, name):
        self.name = name

    def activate(self, device):
        device.turn_on()

    def deactivate(self, device):
        device.turn_off()

    def adjust_temperature(self, device, value):
        return device.set_temperature(value)

    def adjust_brightness(self, device, value):
        return device.set_brightness(value)

    def lock_door(self, door):
        door.lock()

    def unlock_door(self, door):
        door.unlock()
