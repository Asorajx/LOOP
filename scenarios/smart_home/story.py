"""Short terminal stories, code explanations and OOP concepts for the smart home scenario.

Each EXPLAIN entry matches a real method or code line.
Story = what has happened at this step. Code = what the Python line does.
Concept = a relevant OOP idea (only when helpful).
Lines that return True or False can use story_true/story_false and
code_true/code_false so the text matches the real result.

Placeholders: {target} is the chosen device or door, {object} is the object
running the step, and {resident} and {hub} are objects from build(). Each is
replaced by the object's display name.
"""

ACTION_STORIES = {
    "switch_on": "{resident} wants to switch on {target}.",
    "switch_off": "{resident} wants to switch off {target}.",
    "set_temperature": "{resident} wants to set {target} to 23°C.",
    "set_brightness": "{resident} wants to dim {target} to 50%.",
    "lock": "{resident} wants to lock {target}.",
    "unlock": "{resident} wants to unlock {target}.",
}

ACTION_SUMMARIES = {
    "switch_on": {
        "success": {
            "story": "{target} is switched on.",
            "concept": "polymorphism",
            "lesson": "{hub} ran the same line, device.turn_on(), whichever device you picked. Light and "
                      "Fan have their own turn_on(), and Thermostat uses the one it inherits from "
                      "SmartDevice, so each responds in its own way. Try the others.",
        },
    },
    "switch_off": {
        "success": {
            "story": "{target} is switched off.",
            "concept": "inheritance",
            "lesson": "Light and Fan override turn_off() and call the parent's version with super(), "
                      "then reset their own setting. Thermostat inherits SmartDevice's turn_off() unchanged.",
        },
    },
    "set_temperature": {
        "success": {
            "story": "{target} is set to 23°C.",
            "concept": "encapsulation",
            "lesson": "{target} changes its own temperature, and only while it's switched on.",
        },
        "failure": {
            "story": "{resident} cannot change {target}'s temperature because it is switched off.",
            "concept": "methods",
            "lesson": "set_temperature() checked is_on first and returned False without changing "
                      "anything. Switch {target} on and try again.",
        },
    },
    "set_brightness": {
        "success": {
            "story": "{target} is dimmed to 50%.",
            "concept": "methods",
            "lesson": "set_brightness() checks that the light is on before changing anything, then "
                      "returns True to say it worked.",
        },
        "failure": {
            "story": "{resident} cannot dim {target} because it is switched off.",
            "concept": "methods",
            "lesson": "set_brightness() checked is_on first and returned False without changing "
                      "anything. Switch {target} on and try again.",
        },
    },
    "lock": {
        "success": {
            "story": "{target} is locked.",
            "concept": "inheritance",
            "lesson": "{target} is a DoorLock, which doesn't inherit from SmartDevice. It has no is_on "
                      "attribute or turn_on() method, only its own lock() and unlock().",
        },
    },
    "unlock": {
        "success": {
            "story": "{target} is unlocked.",
            "concept": "relationships",
            "lesson": "{resident} asked {hub}, and {hub} asked {target}. Objects work together by "
                      "calling each other's methods, rather than changing each other's attributes.",
        },
    },
}

EXPLAIN = {
    "Resident.switch_on": {
        "call": {
            "story": "{resident} starts a request to switch on {target}.",
            "code": "Start {resident}'s switch_on() method for {target}.",
        },
        "hub.activate(device)": {
            "story": "{resident} asks {hub} to switch on {target}.",
            "code": "Call {hub}'s activate() method with {target}.",
            "concept": "relationships",
            "detail": "{resident} calls {hub}'s method. {hub} then asks the chosen device to act.",
        },
    },
    "Resident.switch_off": {
        "call": {
            "story": "{resident} starts a request to switch off {target}.",
            "code": "Start {resident}'s switch_off() method for {target}.",
        },
        "hub.deactivate(device)": {
            "story": "{resident} asks {hub} to switch off {target}.",
            "code": "Call {hub}'s deactivate() method with {target}.",
        },
    },
    "Resident.set_temperature": {
        "call": {
            "story": "{resident} starts a request to set {target} to 23°C.",
            "code": "Start {resident}'s set_temperature() method for {target}.",
        },
        "return hub.adjust_temperature(device, value)": {
            "story": "{resident} asks {hub} to set {target} to 23°C.",
            "code": "Call {hub}'s adjust_temperature() method with {target} and 23, then return its answer.",
        },
    },
    "Resident.set_brightness": {
        "call": {
            "story": "{resident} starts a request to dim {target} to 50%.",
            "code": "Start {resident}'s set_brightness() method for {target}.",
        },
        "return hub.adjust_brightness(device, value)": {
            "story": "{resident} asks {hub} to set {target} to 50% brightness.",
            "code": "Call {hub}'s adjust_brightness() method with {target} and 50, then return its answer.",
        },
    },
    "Resident.lock_door": {
        "call": {
            "story": "{resident} starts a request to lock {target}.",
            "code": "Start {resident}'s lock_door() method for {target}.",
        },
        "hub.lock_door(door)": {
            "story": "{resident} asks {hub} to lock {target}.",
            "code": "Call {hub}'s lock_door() method with {target}.",
        },
    },
    "Resident.unlock_door": {
        "call": {
            "story": "{resident} starts a request to unlock {target}.",
            "code": "Start {resident}'s unlock_door() method for {target}.",
        },
        "hub.unlock_door(door)": {
            "story": "{resident} asks {hub} to unlock {target}.",
            "code": "Call {hub}'s unlock_door() method with {target}.",
        },
    },
    "HomeHub.activate": {
        "call": {
            "story": "{hub} receives the request to switch on {target}.",
            "code": "Start {hub}'s activate() method for {target}.",
        },
        "device.turn_on()": {
            "story": "{hub} asks {target} to switch on.",
            "code": "Call {target}'s turn_on() method.",
            "concept": "polymorphism",
            "detail": "{hub} uses the same turn_on() call for a Light, Fan or Thermostat. The class of "
                      "{target} decides which turn_on() runs.",
        },
    },
    "HomeHub.deactivate": {
        "call": {
            "story": "{hub} receives the request to switch off {target}.",
            "code": "Start {hub}'s deactivate() method for {target}.",
        },
        "device.turn_off()": {
            "story": "{hub} asks {target} to switch off.",
            "code": "Call {target}'s turn_off() method.",
            "concept": "polymorphism",
            "detail": "{hub} uses the same turn_off() call for a Light, Fan or Thermostat. The class of "
                      "{target} decides which turn_off() runs.",
        },
    },
    "HomeHub.adjust_temperature": {
        "call": {
            "story": "{hub} receives the temperature request for {target}.",
            "code": "Start {hub}'s adjust_temperature() method for {target}.",
        },
        "return device.set_temperature(value)": {
            "story": "{hub} asks {target} to change its temperature.",
            "code": "Call {target}'s set_temperature() method with 23, then return its answer.",
        },
    },
    "HomeHub.adjust_brightness": {
        "call": {
            "story": "{hub} receives the brightness request for {target}.",
            "code": "Start {hub}'s adjust_brightness() method for {target}.",
        },
        "return device.set_brightness(value)": {
            "story": "{hub} asks {target} to change its brightness.",
            "code": "Call {target}'s set_brightness() method with 50, then return its answer.",
        },
    },
    "HomeHub.lock_door": {
        "call": {
            "story": "{hub} receives the request to lock {target}.",
            "code": "Start {hub}'s lock_door() method for {target}.",
        },
        "door.lock()": {
            "story": "{hub} asks {target} to lock itself.",
            "code": "Call {target}'s lock() method.",
        },
    },
    "HomeHub.unlock_door": {
        "call": {
            "story": "{hub} receives the request to unlock {target}.",
            "code": "Start {hub}'s unlock_door() method for {target}.",
        },
        "door.unlock()": {
            "story": "{hub} asks {target} to unlock itself.",
            "code": "Call {target}'s unlock() method.",
        },
    },
    "SmartDevice.turn_on": {
        "call": {
            "story": "{target} starts switching on.",
            "code": "Start the turn_on() method that {object} inherits from SmartDevice.",
            "concept": "inheritance",
            "detail": "A child class gets its parent's methods without writing them again. The Thermostat "
                      "class has no turn_on() of its own, so Python runs SmartDevice's turn_on() on {object}.",
        },
        "super": {
            "story": "{target}'s power is being switched on.",
            "code": "Start SmartDevice.turn_on(). {object}'s own turn_on() called it with super(), "
                    "on the same object.",
            "concept": "inheritance",
            "detail": "super() runs the parent class's version of a method on the same object. {object} "
                      "reuses the SmartDevice code, then its own method adds its own setting.",
        },
        "self.is_on = True": {
            "story": "{target} is now switched on.",
            "code": "Set {target}'s is_on attribute to True.",
        },
    },
    "SmartDevice.turn_off": {
        "call": {
            "story": "{target} starts switching off.",
            "code": "Start the turn_off() method that {object} inherits from SmartDevice.",
            "concept": "inheritance",
            "detail": "The Thermostat class has no turn_off() of its own, so Python runs SmartDevice's "
                      "turn_off() on {object}.",
        },
        "super": {
            "story": "{target}'s power is being switched off.",
            "code": "Start SmartDevice.turn_off(). {object}'s own turn_off() called it with super(), "
                    "on the same object.",
        },
        "self.is_on = False": {
            "story": "{target} is now switched off.",
            "code": "Set {target}'s is_on attribute to False.",
        },
    },
    "Light.turn_on": {
        "call": {
            "story": "{target} begins switching on.",
            "code": "Start the Light class's own turn_on() method.",
            "concept": "inheritance",
            "detail": "Light overrides turn_on() with its own version. That version calls the parent's "
                      "turn_on() with super(), then sets the brightness.",
        },
        "super().turn_on()": {
            "story": "{target} starts by switching its power on.",
            "code": "Call the parent SmartDevice.turn_on() method using super().",
        },
        "self.brightness = 100": {
            "story": "{target} lights up at full brightness.",
            "code": "Set {target}'s brightness attribute to 100.",
        },
    },
    "Light.turn_off": {
        "call": {
            "story": "{target} begins switching off.",
            "code": "Start the Light class's own turn_off() method.",
            "concept": "inheritance",
            "detail": "Light overrides turn_off() too. Its version calls the parent's turn_off() with "
                      "super(), then sets the brightness back to 0.",
        },
        "super().turn_off()": {
            "story": "{target} starts by switching its power off.",
            "code": "Call the parent SmartDevice.turn_off() method using super().",
        },
        "self.brightness = 0": {
            "story": "{target} is now dark.",
            "code": "Set {target}'s brightness attribute to 0.",
        },
    },
    "Light.set_brightness": {
        "call": {
            "story": "{target} receives the request to change its brightness.",
            "code": "Start {target}'s set_brightness() method with the value 50.",
        },
        "if not self.is_on:": {
            "story": "{target} checks whether it is switched on.",
            "code": "Check {target}'s is_on attribute. If {target} is off, its brightness cannot change.",
        },
        "return False": {
            "story": "{target} is off, so its brightness cannot change.",
            "code": "Return False because {target} is switched off.",
        },
        "self.brightness = value": {
            "story": "{target} is now set to 50% brightness.",
            "code": "Set {target}'s brightness attribute to the requested value, 50.",
            "concept": "encapsulation",
            "detail": "{target} changes its own brightness when {hub} asks it to. {hub} does not change "
                      "the attribute directly.",
        },
        "return True": {
            "story": "{target} confirms the brightness was changed.",
            "code": "Return True to confirm the brightness was changed.",
        },
    },
    "Fan.turn_on": {
        "call": {
            "story": "{target} begins switching on.",
            "code": "Start the Fan class's own turn_on() method.",
            "concept": "inheritance",
            "detail": "Fan overrides turn_on() with its own version. That version calls the parent's "
                      "turn_on() with super(), then sets the speed.",
        },
        "super().turn_on()": {
            "story": "{target} starts by switching its power on.",
            "code": "Call the parent SmartDevice.turn_on() method using super().",
        },
        "self.speed = 1": {
            "story": "{target} starts spinning at speed 1.",
            "code": "Set {target}'s speed attribute to 1.",
        },
    },
    "Fan.turn_off": {
        "call": {
            "story": "{target} begins switching off.",
            "code": "Start the Fan class's own turn_off() method.",
            "concept": "inheritance",
            "detail": "Fan overrides turn_off() too. Its version calls the parent's turn_off() with "
                      "super(), then sets the speed back to 0.",
        },
        "super().turn_off()": {
            "story": "{target} starts by switching its power off.",
            "code": "Call the parent SmartDevice.turn_off() method using super().",
        },
        "self.speed = 0": {
            "story": "{target} stops spinning.",
            "code": "Set {target}'s speed attribute to 0.",
        },
    },
    "Thermostat.set_temperature": {
        "call": {
            "story": "{target} receives the request to change its temperature.",
            "code": "Start {target}'s set_temperature() method with the value 23.",
        },
        "if not self.is_on:": {
            "story": "{target} checks whether it is switched on.",
            "code": "Check {target}'s is_on attribute. If {target} is off, its temperature cannot change.",
        },
        "return False": {
            "story": "{target} is off, so its temperature cannot change.",
            "code": "Return False because {target} is switched off.",
        },
        "self.temperature = value": {
            "story": "{target} changes its temperature to 23°C.",
            "code": "Set {target}'s temperature attribute to the requested value, 23.",
            "concept": "encapsulation",
            "detail": "{target} changes its own temperature when {hub} asks it to. {hub} does not change "
                      "the attribute directly.",
        },
        "return True": {
            "story": "{target} confirms the temperature was changed.",
            "code": "Return True to confirm the temperature was changed.",
        },
    },
    "DoorLock.lock": {
        "call": {
            "story": "{target} receives the lock request.",
            "code": "Start {target}'s lock() method.",
        },
        "self.locked = True": {
            "story": "{target} is now locked.",
            "code": "Set {target}'s locked attribute to True.",
        },
    },
    "DoorLock.unlock": {
        "call": {
            "story": "{target} receives the unlock request.",
            "code": "Start {target}'s unlock() method.",
        },
        "self.locked = False": {
            "story": "{target} is now unlocked.",
            "code": "Set {target}'s locked attribute to False.",
        },
    },
}
