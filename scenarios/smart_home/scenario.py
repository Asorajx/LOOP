"""Smart home scenario: a resident controls devices and a door lock through a home hub."""

from engine.scenario_manager import TARGET

from . import story
from .devices import DoorLock, Fan, Light, SmartDevice, Thermostat
from .hub import HomeHub
from .resident import Resident

TITLE = "Smart Home"
ORDER = 3

PANELS = [
    ("Resident", [Resident]),
    ("Home Hub", [HomeHub]),
    ("Devices", [SmartDevice, Light, Fan, Thermostat, DoorLock]),
]

# Attributes shown as small status icons. An icon lights up when the value differs
# from "normal". "icon" names one of the icons in web/js/icons.js.
STATUS = {
    "is_on": {"normal": False, "label": "Switched on", "icon": "power", "tone": "good",
              "about": "The device is powered on."},
    "locked": {"normal": True, "label": "Unlocked", "icon": "lock", "tone": "warning",
               "about": "Anyone can open the door until it's locked again."},
}

POWERED = ["LIGHT001", "FAN001", "THERMO001"]

# Temperature and brightness use fixed values: the Playground picks targets, not arguments.
ACTIONS = [
    {"id": "switch_on", "method": "Resident.switch_on", "targets": POWERED,
     "call": ("resident", "switch_on", "hub", TARGET)},
    {"id": "switch_off", "method": "Resident.switch_off", "targets": POWERED,
     "call": ("resident", "switch_off", "hub", TARGET)},
    {"id": "set_temperature", "method": "Resident.set_temperature", "targets": ["THERMO001"],
     "call": ("resident", "set_temperature", "hub", TARGET, 23)},
    {"id": "set_brightness", "method": "Resident.set_brightness", "targets": ["LIGHT001"],
     "call": ("resident", "set_brightness", "hub", TARGET, 50)},
    {"id": "lock", "method": "Resident.lock_door", "targets": ["DOOR001"],
     "call": ("resident", "lock_door", "hub", TARGET)},
    {"id": "unlock", "method": "Resident.unlock_door", "targets": ["DOOR001"],
     "call": ("resident", "unlock_door", "hub", TARGET)},
]


def build():
    return {
        "resident": Resident("Home Owner"),
        "hub": HomeHub("Main Hub"),
        "LIGHT001": Light("Living Room Light"),
        "FAN001": Fan("Bedroom Fan"),
        "THERMO001": Thermostat("Hallway Thermostat"),
        "DOOR001": DoorLock("Front Door"),
    }
