"""Storyboard, code explanations and OOP concepts for the smart home scenario.

Same format as scenarios/cybersecurity/story.py: EXPLAIN is keyed by method, then by
"call", "super", "property" or the exact text of a line in that method.
"super" belongs to the parent method that super() enters (SmartDevice.turn_on), not the
child that calls it. Tests check that every key matches the real source.
"""

ACTION_STORIES = {
    "switch_on": "Resident asks Home Hub to switch on {target}.",
    "switch_off": "Resident asks Home Hub to switch off {target}.",
    "set_temperature": "Resident tries to set {target} to 23°C.",
    "set_brightness": "Resident tries to dim {target} to 50%.",
    "lock": "Resident asks Home Hub to lock {target}.",
    "unlock": "Resident asks Home Hub to unlock {target}.",
}

# Shown when an action finishes: the result, and the one idea to remember.
ACTION_SUMMARIES = {
    "switch_on": {
        "story": "{target} is switched on.",
        "concept": "polymorphism",
        "lesson": "Home Hub ran the same line, device.turn_on(), whichever device you picked. Light and Fan have their own turn_on(), and Thermostat uses the one it inherits, so each responds in its own way. Try the others.",
    },
    "switch_off": {
        "story": "{target} is switched off.",
        "concept": "inheritance",
        "lesson": "Light and Fan extend turn_off() with super() to also reset their own setting. Thermostat inherits SmartDevice's turn_off() unchanged.",
    },
    "set_temperature": {
        "story": "{target} is set to 23°C.",
        "concept": "encapsulation",
        "lesson": "Thermostat changes its own temperature, and only while it's switched on.",
    },
    "set_brightness": {
        "story": "{target} is dimmed to 50%.",
        "concept": "methods",
        "lesson": "set_brightness() checks that the light is on before changing anything, then returns True to say it worked.",
    },
    "lock": {
        "story": "{target} is locked.",
        "concept": "relationships",
        "lesson": "Resident asked Home Hub, and Home Hub asked the DoorLock. DoorLock isn't a SmartDevice: it has no power, just its own lock() and unlock().",
    },
    "unlock": {
        "story": "{target} is unlocked.",
        "concept": "relationships",
        "lesson": "Objects work together by calling each other's methods, rather than changing each other's attributes.",
    },
}

# Shown instead when an action's method returns False (only the two setting actions can).
FALSE_SUMMARY = {
    "story": "{target} is switched off, so nothing changed.",
    "concept": "methods",
    "lesson": "The method checked is_on first and returned False without changing anything. Switch {target} on and try again.",
}

EXPLAIN = {
    "Resident.switch_on": {
        "hub.activate(device)": {
            "code": "Resident doesn't need to know how each device switches on. It just asks Home Hub.",
            "concept": "relationships",
            "detail": "Objects work together by calling each other's methods.",
        },
    },
    "HomeHub.activate": {
        "device.turn_on()": {
            "code": "This one line works for a Light, a Fan or a Thermostat.",
            "concept": "polymorphism",
            "detail": "Python runs the turn_on() that belongs to the actual device object, so the same call can do different things.",
        },
    },
    "HomeHub.deactivate": {
        "device.turn_off()": {
            "code": "The same line again: each device's own turn_off() runs.",
        },
    },
    "SmartDevice.turn_on": {
        "call": {
            "code": "{object} has no turn_on() of its own, so Python runs the one it inherits from SmartDevice.",
            "concept": "inheritance",
            "detail": "A child class gets its parent's methods without writing them again.",
        },
        "super": {
            "code": "This is SmartDevice's turn_on(), running because {object}'s own turn_on() called super().",
            "concept": "inheritance",
            "detail": "super() runs the parent's version of a method on the same object, so the child can add to it instead of rewriting it.",
        },
        "self.is_on = True": {
            "story": "{target} has power.",
        },
    },
    "SmartDevice.turn_off": {
        "call": {
            "code": "{object} has no turn_off() of its own, so Python runs the one it inherits from SmartDevice.",
        },
        "super": {
            "code": "SmartDevice's turn_off(), running because {object}'s own turn_off() called super().",
        },
        "self.is_on = False": {
            "story": "{target} has no power.",
        },
    },
    "Light.turn_on": {
        "call": {
            "code": "Light has its own turn_on(), so Python runs it instead of SmartDevice's.",
            "concept": "inheritance",
            "detail": "A child class can replace a parent's method with its own version. This is called overriding.",
        },
        "super().turn_on()": {
            "code": "First it runs the parent's turn_on(), which switches the power on.",
        },
        "self.brightness = 100": {
            "story": "{target} lights up at full brightness.",
            "code": "Then it does the one extra thing a Light needs.",
        },
    },
    "Light.turn_off": {
        "self.brightness = 0": {
            "story": "{target} goes dark.",
        },
    },
    "Light.set_brightness": {
        "if not self.is_on:": {
            "code": "A light that's off can't be dimmed.",
        },
        "self.brightness = value": {
            "story": "{target} is dimmed to 50%.",
        },
    },
    "Fan.turn_on": {
        "call": {
            "code": "Fan has its own turn_on() too, so this one runs instead of SmartDevice's.",
        },
        "super().turn_on()": {
            "code": "Like Light, it reuses the parent's turn_on() first.",
        },
        "self.speed = 1": {
            "story": "{target} starts spinning at speed 1.",
            "code": "Then it does the one extra thing a Fan needs.",
        },
    },
    "Fan.turn_off": {
        "self.speed = 0": {
            "story": "{target} stops spinning.",
        },
    },
    "Thermostat.set_temperature": {
        "if not self.is_on:": {
            "code": "Thermostat doesn't accept a new temperature while it's off.",
        },
        "self.temperature = value": {
            "story": "{target} is set to 23°C.",
            "code": "Thermostat changes its own attribute, through its own method.",
            "concept": "encapsulation",
            "detail": "An object manages its own state: other objects ask it to change, rather than changing its attributes directly.",
        },
    },
    "DoorLock.lock": {
        "self.locked = True": {
            "story": "{target} is locked.",
        },
    },
    "DoorLock.unlock": {
        "self.locked = False": {
            "story": "{target} is unlocked.",
        },
    },
}
