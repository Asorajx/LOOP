import inspect
import textwrap
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from attacks import (
    CredentialAttack,
    MitMAttack,
    DoSAttack,
    DDoSAttack,
    MalwareAttack,
    RansomwareAttack
)
from actors import Attacker, Defender
from network import NetworkDevice, Connection
from simulation import CyberDefenseSimulation


# =========================
# FastAPI Application
# =========================

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"


# =========================
# Simulation Objects
# =========================

device1 = NetworkDevice("DEV001", "Web Server")
device2 = NetworkDevice("DEV002", "Database Server")

connection = Connection("CON001", device1, device2)

credential = CredentialAttack()
mitm = MitMAttack()
dos = DoSAttack()
ddos = DDoSAttack()
malware = MalwareAttack()
ransomware = RansomwareAttack()

attacker = Attacker(
    "Attacker 1",
    [
        credential,
        mitm,
        dos,
        ddos,
        malware,
        ransomware
    ]
)

defender = Defender("Defender 1")

simulation = CyberDefenseSimulation(
    attacker,
    defender,
    [device1, device2],
    [connection]
)


# =========================
# Lookups
# =========================

attacks = {
    "credential": credential,
    "mitm": mitm,
    "dos": dos,
    "ddos": ddos,
    "malware": malware,
    "ransomware": ransomware
}

source_methods = {
    "attacker-perform": Attacker.perform_attack,
    "credential-execute": CredentialAttack.execute,
    "mitm-execute": MitMAttack.execute,
    "dos-execute": DoSAttack.execute,
    "ddos-execute": DDoSAttack.execute,
    "malware-execute": MalwareAttack.execute,
    "ransomware-execute": RansomwareAttack.execute,
    "device-increase-risk": NetworkDevice.increase_risk,
    "device-overload": NetworkDevice.overload,
    "device-isolate": NetworkDevice.isolate,
    "device-block": NetworkDevice.block,
    "device-unblock": NetworkDevice.unblock,
    "device-lock-files": NetworkDevice.lock_files,
    "device-restore": NetworkDevice.restore,
    "connection-intercept": Connection.intercept,
    "connection-secure": Connection.secure,
    "connection-block": Connection.block,
    "connection-unblock": Connection.unblock,
    "defender-inspect": Defender.inspect,
    "defender-block": Defender.block,
    "defender-unblock": Defender.unblock,
    "defender-isolate": Defender.isolate,
    "defender-restore": Defender.restore,
    "defender-secure": Defender.secure_connection
}

event_source_ids = {
    ("Attacker", "perform_attack"): "attacker-perform",
    ("CredentialAttack", "execute"): "credential-execute",
    ("MitMAttack", "execute"): "mitm-execute",
    ("DoSAttack", "execute"): "dos-execute",
    ("DDoSAttack", "execute"): "ddos-execute",
    ("MalwareAttack", "execute"): "malware-execute",
    ("RansomwareAttack", "execute"): "ransomware-execute",
    ("NetworkDevice", "increase_risk"): "device-increase-risk",
    ("NetworkDevice", "overload"): "device-overload",
    ("NetworkDevice", "isolate"): "device-isolate",
    ("NetworkDevice", "block"): "device-block",
    ("NetworkDevice", "unblock"): "device-unblock",
    ("NetworkDevice", "lock_files"): "device-lock-files",
    ("NetworkDevice", "restore"): "device-restore",
    ("Connection", "intercept"): "connection-intercept",
    ("Connection", "secure"): "connection-secure",
    ("Connection", "block"): "connection-block",
    ("Connection", "unblock"): "connection-unblock",
    ("Defender", "inspect"): "defender-inspect",
    ("Defender", "block"): "defender-block",
    ("Defender", "unblock"): "defender-unblock",
    ("Defender", "isolate"): "defender-isolate",
    ("Defender", "restore"): "defender-restore",
    ("Defender", "secure_connection"): "defender-secure"
}

attack_sources = {
    "credential-execute": (credential, "DEV001"),
    "mitm-execute": (mitm, "CON001"),
    "dos-execute": (dos, "DEV001"),
    "ddos-execute": (ddos, "DEV001"),
    "malware-execute": (malware, "DEV001"),
    "ransomware-execute": (ransomware, "DEV001")
}


# =========================
# Helper Functions
# =========================

def get_target(target_id):
    for device in simulation.devices:
        if device.device_id == target_id:
            return device

    for connection_item in simulation.connections:
        if connection_item.connection_id == target_id:
            return connection_item

    return None


def get_device(target_id="DEV001"):
    target = get_target(target_id)
    return target if isinstance(target, NetworkDevice) else None


def get_connection(target_id="CON001"):
    target = get_target(target_id)
    return target if isinstance(target, Connection) else None


def get_event_data(event):
    data = event.get_data()
    data["source_id"] = event_source_ids.get(
        (data["class_name"], data["method_name"])
    )
    return data


def get_response(success=True):
    events = [
        get_event_data(event)
        for event in simulation.tracer.events
    ]

    devices = [
        device.get_data()
        for device in simulation.devices
    ]

    connections = [
        connection_item.get_data()
        for connection_item in simulation.connections
    ]

    return {
        "success": success,
        "events": events,
        "devices": devices,
        "connections": connections
    }


def execute_source(source_id, data):
    target_id = data.get("target")

    if source_id == "attacker-perform":
        attack_name = data.get("attack", "credential")
        attack = attacks.get(attack_name)

        if attack is None:
            return False, "Attack not found.", None

        default_target = "CON001" if attack_name == "mitm" else "DEV001"
        target = get_target(target_id or default_target)

        if target is None:
            return False, "Target not found.", None

        return True, "", simulation.perform_attack(attack, target)

    if source_id in attack_sources:
        attack, default_target = attack_sources[source_id]
        target = get_target(target_id or default_target)

        if target is None:
            return False, "Target not found.", None

        attack.execute(target)
        return True, "", None

    device = get_device(target_id or "DEV001")

    if source_id == "device-increase-risk":
        if device is None:
            return False, "Device not found.", None
        device.increase_risk(data.get("amount", 1))
        return True, "", None

    if source_id == "device-overload":
        if device is None:
            return False, "Device not found.", None
        device.overload(data.get("traffic_level", "HIGH"))
        return True, "", None

    if source_id == "device-isolate":
        if device is None:
            return False, "Device not found.", None
        device.isolate()
        return True, "", None

    if source_id == "device-block":
        if device is None:
            return False, "Device not found.", None
        device.block()
        return True, "", None

    if source_id == "device-unblock":
        if device is None:
            return False, "Device not found.", None
        device.unblock()
        return True, "", None

    if source_id == "device-lock-files":
        if device is None:
            return False, "Device not found.", None
        device.lock_files()
        return True, "", None

    if source_id == "device-restore":
        if device is None:
            return False, "Device not found.", None
        device.restore()
        return True, "", None

    connection_target = get_connection(target_id or "CON001")

    if source_id == "connection-intercept":
        if connection_target is None:
            return False, "Connection not found.", None
        connection_target.intercept()
        return True, "", None

    if source_id == "connection-secure":
        if connection_target is None:
            return False, "Connection not found.", None
        connection_target.secure()
        return True, "", None

    if source_id == "connection-block":
        if connection_target is None:
            return False, "Connection not found.", None
        connection_target.block()
        return True, "", None

    if source_id == "connection-unblock":
        if connection_target is None:
            return False, "Connection not found.", None
        connection_target.unblock()
        return True, "", None

    if source_id == "defender-inspect":
        if device is None:
            return False, "Device not found.", None
        return True, "", simulation.inspect(device)

    if source_id == "defender-block":
        if device is None:
            return False, "Device not found.", None
        simulation.block(device)
        return True, "", None

    if source_id == "defender-unblock":
        if device is None:
            return False, "Device not found.", None
        simulation.unblock(device)
        return True, "", None

    if source_id == "defender-isolate":
        if device is None:
            return False, "Device not found.", None
        simulation.isolate(device)
        return True, "", None

    if source_id == "defender-restore":
        if device is None:
            return False, "Device not found.", None
        simulation.restore(device)
        return True, "", None

    if source_id == "defender-secure":
        if connection_target is None:
            return False, "Connection not found.", None
        simulation.secure_connection(connection_target)
        return True, "", None

    return False, "Executable source not found.", None


# =========================
# Source Code
# =========================

@app.get("/api/source/{source_id}")
def get_source(source_id: str):
    method = source_methods.get(source_id)

    if method is None:
        return {
            "success": False,
            "message": "Source not found."
        }

    return {
        "success": True,
        "source": textwrap.dedent(inspect.getsource(method))
    }


# =========================
# State
# =========================

@app.get("/api/state")
def get_state():
    simulation.tracer.clear()
    return get_response()


# =========================
# Method Execution
# =========================

@app.post("/api/execute/{source_id}")
def execute_method(source_id: str, data: dict):
    simulation.tracer.clear()
    success, message, result = execute_source(source_id, data)

    if not success:
        response = get_response(False)
        response["message"] = message
        return response

    response = get_response()
    response["result"] = result
    return response


# =========================
# Existing Attack Route
# =========================

@app.post("/api/attack")
def perform_attack(data: dict):
    simulation.tracer.clear()

    attack_name = data.get("attack")
    target_id = data.get("target")

    attack = attacks.get(attack_name)
    target = get_target(target_id)

    if attack is None:
        return {
            "success": False,
            "message": "Attack not found."
        }

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    result = simulation.perform_attack(attack, target)
    return get_response(result)


# =========================
# Existing Defender Routes
# =========================

@app.post("/api/block")
def block(data: dict):
    simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    simulation.block(target)
    return get_response()


@app.post("/api/unblock")
def unblock(data: dict):
    simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    simulation.unblock(target)
    return get_response()


@app.post("/api/isolate")
def isolate(data: dict):
    simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    simulation.isolate(target)
    return get_response()


@app.post("/api/restore")
def restore(data: dict):
    simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    simulation.restore(target)
    return get_response()


@app.post("/api/secure")
def secure_connection(data: dict):
    simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Connection not found."
        }

    simulation.secure_connection(target)
    return get_response()


# =========================
# Reset
# =========================

@app.post("/api/reset")
def reset():
    simulation.reset()
    return get_response()


# =========================
# Frontend
# =========================

app.mount(
    "/",
    StaticFiles(directory=DOCS_DIR, html=True),
    name="frontend"
)
