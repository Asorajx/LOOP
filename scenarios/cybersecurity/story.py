"""Storyboard, code explanations and OOP concepts for the cybersecurity scenario.

Keep every part short and plain:
    story    what happens, as a simple cause and effect ("Device A is infected.")
    code     why the highlighted line makes it happen (don't repeat the code itself)
    concept  the OOP idea, only on the steps that show it best
    detail   one or two sentences about that idea

EXPLAIN is keyed by method ("Class.method"), then by:
    "call"      entering the method
    "super"     entering the method through super()
    "property"  entering a property getter
    <line>      the exact text of a line in that method
Steps without an entry are still shown, with a short automatic description.

{target} is the chosen target's name (such as "Device A"), {object} is the
running object's name, and {result} (summaries only) is the action's result.
Tests check that every key matches the real source.
"""

ACTION_STORIES = {
    "malware": "Attacker sends malware to {target}.",
    "ransomware": "Attacker sends ransomware to {target}.",
    "intercept": "Attacker tries to secretly read messages between the two devices.",
    "isolate": "Victim disconnects {target} so attacks can't reach it.",
    "recover": "Victim tries to recover {target}.",
    "secure": "Victim secures {target}.",
}

# Shown when an action finishes: the result, and the one idea to remember.
ACTION_SUMMARIES = {
    "malware": {
        "story": "{target} is infected. The other device isn't.",
        "concept": "classes",
        "lesson": "Device A and Device B are two objects made from the same Device class. Each keeps its own attributes, so infecting one doesn't change the other.",
    },
    "ransomware": {
        "story": "{target} is infected and its files are locked.",
        "concept": "inheritance",
        "lesson": "RansomwareAttack is a kind of MalwareAttack. It reused the parent's code with super(), then added one thing of its own: locking the files.",
    },
    "intercept": {
        "story": "Messages between the devices are being read.",
        "concept": "polymorphism",
        "lesson": "The same launch() line ran a third execute(), this time with a Connection instead of a Device. launch() only needs the target to have online, and the attack to have execute().",
    },
    "isolate": {
        "story": "{target} is offline, so attacks can't reach it. The connection is offline too.",
        "concept": "relationships",
        "lesson": "The connection holds both devices and asks them whether they're online. Disconnecting one device changed the connection too. Try Intercept now.",
    },
    "recover": {
        "story": "{target} recovers and is back to normal.",
        "concept": "encapsulation",
        "lesson": "Victim asked the device to recover, and Device's own method reset its attributes. Objects look after their own state.",
    },
    "secure": {
        "story": "The connection is private again.",
        "concept": "methods",
        "lesson": "Victim and Connection both have a method called secure(). Python runs the one that belongs to the object it's called on.",
    },
}

# Used instead of the action's summary when the action returns False.
FALSE_SUMMARY = {
    "story": "{target} is offline, so the attack never reached it.",
    "concept": "methods",
    "lesson": "launch() stopped early with return False, so execute() never ran.",
}

EXPLAIN = {
    # -------------------------
    # Attacker
    # -------------------------
    "Attacker.launch": {
        "if not target.online:": {
            "story": "Attacker checks whether {target} is online.",
        },
        "return False": {
            "story": "{target} is offline, so the attack stops here.",
            "code": "return ends the method, so the lines below never run.",
        },
        "attack.execute(target)": {
            "story": "The attack begins.",
            "code": "launch() calls execute() without checking which attack it has.",
            "concept": "polymorphism",
            "detail": "MalwareAttack, RansomwareAttack and InterceptAttack each have their own execute(). Python runs the one that belongs to the object passed in.",
        },
        "return True": {
            "code": "Reports back that the attack went ahead.",
        },
    },

    # -------------------------
    # Attacks
    # -------------------------
    "MalwareAttack.execute": {
        "call": {
            "code": "attack is a MalwareAttack object, so its execute() runs.",
        },
        "super": {
            "story": "First, it does what all malware does.",
            "code": "This is the parent's execute(), running because the child called super().",
        },
        "target.infect()": {
            "story": "The malware reaches {target}.",
            "code": "The attack asks the device to infect itself, instead of changing its attributes directly.",
            "concept": "encapsulation",
            "detail": "Each object looks after its own state through its own methods. Python doesn't strictly forbid changing another object's attributes, but asking it is clearer and safer.",
        },
    },
    "RansomwareAttack.execute": {
        "call": {
            "code": "RansomwareAttack has its own execute(), so Python runs this one instead of MalwareAttack's.",
            "concept": "inheritance",
            "detail": "A child class can replace a parent's method with its own version. This is called overriding.",
        },
        "super().execute(target)": {
            "code": "super() runs the parent's execute() from MalwareAttack.",
            "concept": "inheritance",
            "detail": "The parent's code only runs because this line asks for it. It runs on the same ransomware object.",
        },
        "target.lock_files()": {
            "story": "Then it locks {target}'s files.",
            "code": "The one thing RansomwareAttack adds after its parent's behaviour.",
        },
    },
    "InterceptAttack.execute": {
        "call": {
            "code": "attack is an InterceptAttack, and this time target is the connection, not a device.",
        },
        "target.intercept()": {
            "story": "Attacker taps into the connection.",
        },
    },

    # -------------------------
    # Device
    # -------------------------
    "Device.infect": {
        "self.infected = True": {
            "story": "{object} is infected.",
            "code": "self is the object the method was called on: {object}.",
            "concept": "methods",
            "detail": "Every Device object shares this method, but self points to one object each time. Only {object}'s infected attribute changes.",
        },
    },
    "Device.lock_files": {
        "self.files_locked = True": {
            "story": "{object}'s files are locked.",
        },
    },
    "Device.disconnect": {
        "self.online = False": {
            "story": "{object} goes offline.",
            "code": "Attacker checks online before every attack.",
        },
    },
    "Device.recover": {
        "call": {
            "concept": "encapsulation",
            "detail": "Victim doesn't reset the device's attributes itself. Device's own recover() knows what needs resetting.",
        },
        "self.online = True": {"story": "{object} is back online."},
        "self.infected = False": {"story": "The infection is removed."},
        "self.files_locked = False": {"story": "The files are unlocked."},
    },

    # -------------------------
    # Connection
    # -------------------------
    "Connection.online": {
        "property": {
            "code": "online looks like an attribute, but it's a property: reading it runs this method.",
        },
        "return self.device_a.online and self.device_b.online": {
            "story": "The connection checks both of its devices.",
            "code": "It's only online while both devices are online.",
            "concept": "relationships",
            "detail": "The connection was given two Device objects when it was created, and keeps them. Its own state depends on theirs.",
        },
    },
    "Connection.intercept": {
        "self.intercepted = True": {
            "story": "Messages on the connection are being read.",
        },
    },
    "Connection.secure": {
        "self.intercepted = False": {
            "story": "Messages are private again.",
        },
    },

    # -------------------------
    # Victim
    # -------------------------
    "Victim.isolate": {
        "device.disconnect()": {
            "story": "Victim disconnects {target} to stop attacks reaching it.",
            "code": "Victim asks the device to disconnect itself.",
        },
    },
    "Victim.recover": {
        "device.recover()": {
            "story": "Victim asks {target} to recover.",
        },
    },
    "Victim.secure": {
        "connection.secure()": {
            "story": "Victim secures the connection.",
            "code": "This calls Connection's secure(), a different method from Victim's own.",
        },
    },
}
