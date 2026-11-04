class SmartDevice:
    def __init__(self, name):
        self.name = name
        self.is_on = False

    def turn_on(self):
        self.is_on = True

    def turn_off(self):
        self.is_on = False


class Light(SmartDevice):
    def __init__(self, name):
        super().__init__(name)
        self.brightness = 0

    def turn_on(self):
        super().turn_on()
        self.brightness = 100

    def turn_off(self):
        super().turn_off()
        self.brightness = 0

    def set_brightness(self, value):
        if not self.is_on:
            return False
        self.brightness = value
        return True


class Fan(SmartDevice):
    def __init__(self, name):
        super().__init__(name)
        self.speed = 0

    def turn_on(self):
        super().turn_on()
        self.speed = 1

    def turn_off(self):
        super().turn_off()
        self.speed = 0


class Thermostat(SmartDevice):
    def __init__(self, name):
        super().__init__(name)
        self.temperature = 22

    def set_temperature(self, value):
        if not self.is_on:
            return False
        self.temperature = value
        return True


class DoorLock:
    def __init__(self, name):
        self.name = name
        self.locked = True

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False
