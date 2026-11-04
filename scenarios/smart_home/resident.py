class Resident:
    def __init__(self, name):
        self.name = name

    def switch_on(self, hub, device):
        hub.activate(device)

    def switch_off(self, hub, device):
        hub.deactivate(device)

    def set_temperature(self, hub, device, value):
        return hub.adjust_temperature(device, value)

    def set_brightness(self, hub, device, value):
        return hub.adjust_brightness(device, value)

    def lock_door(self, hub, door):
        hub.lock_door(door)

    def unlock_door(self, hub, door):
        hub.unlock_door(door)
