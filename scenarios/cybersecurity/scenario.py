"""Cybersecurity scenario: an attacker, two devices on a connection, and a victim."""

from engine.scenario_manager import TARGET

from . import story
from .attacks import Attack, Attacker, InterceptAttack, MalwareAttack, RansomwareAttack
from .devices import Connection, Device
from .victim import Victim

TITLE = "Cybersecurity"
ORDER = 1

PANELS = [
    ("Attacker", [Attacker, Attack, MalwareAttack, RansomwareAttack, InterceptAttack]),
    ("Device", [Device, Connection]),
    ("Victim", [Victim]),
]

# Attributes shown as small status icons. An icon lights up when the value differs
# from "normal". "icon" names one of the icons in web/js/icons.js.
STATUS = {
    "online": {"normal": True, "label": "Offline", "icon": "offline", "tone": "warning",
               "about": "Disconnected, so attacks can't reach it."},
    "infected": {"normal": False, "label": "Infected", "icon": "bug", "tone": "danger",
                 "about": "Malware is running on this device."},
    "files_locked": {"normal": False, "label": "Files locked", "icon": "lock", "tone": "danger",
                     "about": "Ransomware has locked the files."},
    "intercepted": {"normal": False, "label": "Intercepted", "icon": "eye", "tone": "danger",
                    "about": "Someone is secretly reading the messages."},
}

DEVICES = ["DEV001", "DEV002"]
CONNECTIONS = ["CON001"]

# Each action starts from the def line named in "method": clicking that line in the
# Playground runs the action. "call" is (object, method, arguments...); TARGET is
# replaced by the chosen target, and other strings are object labels from build().
ACTIONS = [
    {"id": "malware", "method": "MalwareAttack.execute", "targets": DEVICES,
     "call": ("attacker", "launch", "malware", TARGET)},
    {"id": "ransomware", "method": "RansomwareAttack.execute", "targets": DEVICES,
     "call": ("attacker", "launch", "ransomware", TARGET)},
    {"id": "intercept", "method": "InterceptAttack.execute", "targets": CONNECTIONS,
     "call": ("attacker", "launch", "intercept", TARGET)},
    {"id": "isolate", "method": "Victim.isolate", "targets": DEVICES,
     "call": ("victim", "isolate", TARGET)},
    {"id": "recover", "method": "Victim.recover", "targets": DEVICES,
     "call": ("victim", "recover", TARGET)},
    {"id": "secure", "method": "Victim.secure", "targets": CONNECTIONS,
     "call": ("victim", "secure", TARGET)},
]


def build():
    device_a = Device("Device A")
    device_b = Device("Device B")

    return {
        "attacker": Attacker("Remote Attacker"),
        "malware": MalwareAttack(),
        "ransomware": RansomwareAttack(),
        "intercept": InterceptAttack(),
        "DEV001": device_a,
        "DEV002": device_b,
        "CON001": Connection("the connection", device_a, device_b),
        "victim": Victim("Device Owner"),
    }
