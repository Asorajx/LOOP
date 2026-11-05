"""Short terminal stories, code explanations and OOP concepts for the cybersecurity scenario.

Each EXPLAIN entry matches a real method or code line.
Story = what has happened at this step. Code = what the Python line does.
Concept = a relevant OOP idea (only when helpful).
Lines that return True or False can use story_true/story_false and
code_true/code_false so the text matches the real result.

Placeholders: {target} is the chosen device or connection, {object} is the
object running the step, and {attacker}, {victim}, {DEV001}, {DEV002} and
{CON001} are objects from build(). Each is replaced by the object's display name.
"""

# Shared by every attack: launch() stops before execute() when the target is offline.
OFFLINE_DEVICE = {
    "concept": "methods",
    "lesson": "launch() read {target}'s online attribute first and stopped early with return False, "
              "so the attack's execute() method never ran and {target} wasn't changed.",
}

ACTION_STORIES = {
    "malware": "{attacker} tries to send malware to {target}.",
    "ransomware": "{attacker} tries to send ransomware to {target}.",
    "intercept": "{attacker} tries to secretly read messages sent over {target}.",
    "isolate": "{victim} disconnects {target} so attacks can't reach it.",
    "recover": "{victim} recovers {target}.",
    "secure": "{victim} secures {target}.",
}

ACTION_SUMMARIES = {
    "malware": {
        "success": {
            "story": "{target} is infected. The other device keeps its own state.",
            "concept": "classes",
            "lesson": "{DEV001} and {DEV002} are two objects made from the same Device class. Each keeps "
                      "its own attributes, so infecting one doesn't change the other.",
        },
        "failure": {"story": "{target} is offline, so the malware never reached it.", **OFFLINE_DEVICE},
    },
    "ransomware": {
        "success": {
            "story": "{target} is infected and its files are locked.",
            "concept": "inheritance",
            "lesson": "RansomwareAttack is a kind of MalwareAttack. It reused the parent's code with "
                      "super(), then added one thing of its own: locking the files.",
        },
        "failure": {"story": "{target} is offline, so the ransomware never reached it.", **OFFLINE_DEVICE},
    },
    "intercept": {
        "success": {
            "story": "Messages on {target} are now being intercepted.",
            "concept": "polymorphism",
            "lesson": "launch() ran the same line, attack.execute(target), but this time Python used "
                      "InterceptAttack's execute(). The target can be a Device or a Connection, because "
                      "launch() only needs it to have an online value.",
        },
        "failure": {
            "story": "{target} is offline because at least one device is disconnected, so the attack never reached it.",
            "concept": "properties",
            "lesson": "The connection's online value is a property worked out from both devices. "
                      "Disconnecting one device was enough to make launch() stop with return False.",
        },
    },
    "isolate": {
        "success": {
            "story": "{target} is offline, so attacks can't reach it. {CON001} is offline too.",
            "concept": "relationships",
            "lesson": "{CON001} holds references to both devices and works out its online value from "
                      "them. Disconnecting one device changed the connection too. Try Intercept now.",
        },
    },
    "recover": {
        "success": {
            "story": "{target} is back to normal: online, not infected, and its files are unlocked.",
            "concept": "encapsulation",
            "lesson": "{victim} asked {target} to recover, and the Device's own recover() method reset "
                      "its attributes. Objects look after their own state.",
        },
    },
    "secure": {
        "success": {
            "story": "Messages on {target} are no longer being intercepted.",
            "concept": "methods",
            "lesson": "The Victim and Connection classes both have a method called secure(). Python runs "
                      "the one that belongs to the object it's called on.",
        },
    },
}

EXPLAIN = {
    "Attacker.launch": {
        "call": {
            "story": "{attacker} prepares an attack on {target}.",
            "code": "Start {attacker}'s launch() method with the chosen attack and {target}.",
        },
        "if not target.online:": {
            "story": "{attacker} checks whether {target} is online.",
            "code": "Read {target}'s online value. If {target} is offline, the attack stops here.",
        },
        "return False": {
            "story": "{target} is offline, so the attack stops.",
            "code": "Return False to show that the attack did not happen.",
        },
        "attack.execute(target)": {
            "story": "{attacker} starts the chosen attack on {target}.",
            "code": "Call the chosen attack object's execute() method with {target}.",
            "concept": "polymorphism",
            "detail": "Each attack class has its own execute() method. Python uses the version belonging "
                      "to the chosen attack object.",
        },
        "return True": {
            "story": "{attacker} confirms that the attack was carried out.",
            "code": "Return True to show that the attack was carried out.",
        },
    },
    "MalwareAttack.execute": {
        "call": {
            "story": "The malware attack starts on {target}.",
            "code": "Start MalwareAttack's execute() method with {target}.",
            "concept": "abstraction",
            "detail": "An abstract class defines methods that its subclasses must have. For example, the "
                      "Attack class requires every attack subclass to have an execute() method. "
                      "MalwareAttack provides its own execute(), which infects the target.",
        },
        "super": {
            "story": "The infection part of the attack begins on {target}.",
            "code": "Start MalwareAttack.execute(). RansomwareAttack called it with super(), "
                    "on the same ransomware object.",
        },
        "target.infect()": {
            "story": "The attack tells {target} to become infected.",
            "code": "Call {target}'s infect() method.",
            "concept": "encapsulation",
            "detail": "{target} changes its own infected attribute through its infect() method. The attack "
                      "does not change that attribute directly.",
        },
    },
    "RansomwareAttack.execute": {
        "call": {
            "story": "The ransomware attack starts on {target}.",
            "code": "Start RansomwareAttack's own execute() method with {target}.",
            "concept": "inheritance",
            "detail": "RansomwareAttack overrides execute(): it has its own version instead of the one in "
                      "MalwareAttack. Its version still runs the parent's code by calling super().",
        },
        "super().execute(target)": {
            "story": "The ransomware attack first infects {target}.",
            "code": "Call the parent MalwareAttack.execute() method with {target}, using super().",
            "concept": "inheritance",
            "detail": "RansomwareAttack inherits from MalwareAttack. super() runs the parent's version on "
                      "the same object, so ransomware reuses the infection code before adding file locking.",
        },
        "target.lock_files()": {
            "story": "The ransomware attack tells {target} to lock its files.",
            "code": "Call {target}'s lock_files() method.",
        },
    },
    "InterceptAttack.execute": {
        "call": {
            "story": "The intercept attack starts on {target}.",
            "code": "Start InterceptAttack's execute() method with {target}.",
        },
        "target.intercept()": {
            "story": "The intercept attack targets the messages on {target}.",
            "code": "Call {target}'s intercept() method.",
        },
    },
    "Device.infect": {
        "call": {
            "story": "{object} receives the instruction to become infected.",
            "code": "Start {object}'s infect() method.",
        },
        "self.infected = True": {
            "story": "{object} is now infected.",
            "code": "Set {object}'s infected attribute to True.",
            "concept": "attributes",
            "detail": "Each Device object has its own infected attribute. Changing {object} does not "
                      "infect the other device.",
        },
    },
    "Device.lock_files": {
        "call": {
            "story": "{object} receives the instruction to lock its files.",
            "code": "Start {object}'s lock_files() method.",
        },
        "self.files_locked = True": {
            "story": "{object}'s files are now locked.",
            "code": "Set {object}'s files_locked attribute to True.",
        },
    },
    "Device.disconnect": {
        "call": {
            "story": "{object} receives the instruction to disconnect.",
            "code": "Start {object}'s disconnect() method.",
        },
        "self.online = False": {
            "story": "{object} is now offline, so {CON001} is offline too.",
            "code": "Set {object}'s online attribute to False.",
            "concept": "properties",
            "detail": "online is a stored attribute on {object}, but on the connection it's a property. "
                      "No Connection code ran, yet its online value changed, because Python works it out "
                      "from the two devices each time it's read.",
        },
    },
    "Device.recover": {
        "call": {
            "story": "{object} starts recovering.",
            "code": "Start {object}'s recover() method.",
            "concept": "encapsulation",
            "detail": "{victim} doesn't reset {object}'s attributes itself. The Device's own recover() "
                      "method knows what needs resetting.",
        },
        "self.online = True": {
            "story": "{object} is now online.",
            "code": "Set {object}'s online attribute to True.",
        },
        "self.infected = False": {
            "story": "{object} is no longer infected.",
            "code": "Set {object}'s infected attribute to False.",
        },
        "self.files_locked = False": {
            "story": "{object}'s files are unlocked.",
            "code": "Set {object}'s files_locked attribute to False.",
        },
    },
    "Connection.online": {
        "property": {
            "story": "{object} checks whether both devices are online.",
            "code": "Run {object}'s online property method to check whether both devices are online.",
            "concept": "properties",
            "detail": "online looks like an attribute, but on a Connection it's a property. Python runs "
                      "this method each time it's read, so the value always matches the two devices.",
        },
        "return self.device_a.online and self.device_b.online": {
            "story": "{object} checks the status of {DEV001} and {DEV002}.",
            "code": "Return True only if {DEV001} and {DEV002} are both online.",
            "story_true": "Both devices are online, so {object} is online.",
            "story_false": "At least one device is offline, so {object} is offline.",
            "code_true": "{DEV001} and {DEV002} are both online, so return True.",
            "code_false": "At least one of {DEV001} and {DEV002} is offline, so return False.",
            "concept": "relationships",
            "detail": "The connection was given two Device objects when it was created, and keeps "
                      "references to them. Its own state depends on theirs.",
        },
    },
    "Connection.intercept": {
        "call": {
            "story": "{object} receives the interception request.",
            "code": "Start {object}'s intercept() method.",
        },
        "self.intercepted = True": {
            "story": "Messages on {object} are now being intercepted.",
            "code": "Set {object}'s intercepted attribute to True.",
        },
    },
    "Connection.secure": {
        "call": {
            "story": "{object} receives the request to secure its messages.",
            "code": "Start {object}'s secure() method.",
        },
        "self.intercepted = False": {
            "story": "Messages on {object} are no longer being intercepted.",
            "code": "Set {object}'s intercepted attribute to False.",
        },
    },
    "Victim.isolate": {
        "call": {
            "story": "{victim} starts isolating {target}.",
            "code": "Start {victim}'s isolate() method for {target}.",
        },
        "device.disconnect()": {
            "story": "{victim} asks {target} to disconnect.",
            "code": "Call {target}'s disconnect() method.",
        },
    },
    "Victim.recover": {
        "call": {
            "story": "{victim} starts recovering {target}.",
            "code": "Start {victim}'s recover() method for {target}.",
        },
        "device.recover()": {
            "story": "{victim} asks {target} to recover.",
            "code": "Call {target}'s recover() method.",
        },
    },
    "Victim.secure": {
        "call": {
            "story": "{victim} starts securing {target}.",
            "code": "Start {victim}'s secure() method for {target}.",
        },
        "connection.secure()": {
            "story": "{victim} asks {target} to secure its messages.",
            "code": "Call {target}'s secure() method.",
        },
    },
}
