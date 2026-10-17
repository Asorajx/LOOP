import inspect
import textwrap
from pathlib import Path
from collections import defaultdict, deque
from contextvars import ContextVar
from dataclasses import dataclass, field
import asyncio
import secrets
import time
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from fastapi import Request
from fastapi.responses import JSONResponse

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
# Validated request types
# =========================

class TargetPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: Literal["DEV001", "DEV002", "CON001"]

class AttackPayload(TargetPayload):
    attack: Literal["credential", "mitm", "dos", "ddos", "malware", "ransomware"]

class ExecutePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: Literal["DEV001", "DEV002", "CON001"] | None = None
    attack: Literal["credential", "mitm", "dos", "ddos", "malware", "ransomware"] | None = None
    amount: StrictInt = Field(default=1, ge=0, le=3)
    traffic_level: Literal["NORMAL", "HIGH", "CRITICAL"] = "HIGH"


# =========================
# Independent simulation sessions
# =========================

@dataclass
class Session:
    simulation: CyberDefenseSimulation
    attacks: dict
    last_seen: float
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


def new_session() -> Session:
    device1 = NetworkDevice("DEV001", "Web Server")
    device2 = NetworkDevice("DEV002", "Database Server")
    connection = Connection("CON001", device1, device2)
    attacks = {
        "credential": CredentialAttack(),
        "mitm": MitMAttack(),
        "dos": DoSAttack(),
        "ddos": DDoSAttack(),
        "malware": MalwareAttack(),
        "ransomware": RansomwareAttack(),
    }
    attacker = Attacker("Attacker 1", list(attacks.values()))
    defender = Defender("Defender 1")
    simulation = CyberDefenseSimulation(attacker, defender, [device1, device2], [connection])
    return Session(simulation, attacks, time.monotonic())


SESSION_COOKIE = "loop_session"
SESSION_TTL_SECONDS = 60 * 60
MAX_SESSIONS = 1000
SESSIONS = {}
SESSION_CONTEXT = ContextVar("loop_session_context", default=None)
# Lightweight in-process limits. For multi-worker/multi-instance deployments use
# a shared Redis-backed store instead.
IP_ATTEMPTS = defaultdict(deque)
SESSION_ATTEMPTS = defaultdict(deque)
RATE_WINDOW = 60
IP_LIMIT = 240
SESSION_LIMIT = 100


def current_session() -> Session:
    session = SESSION_CONTEXT.get()
    if session is None:
        raise RuntimeError("A simulation session is required")
    return session


def within_limit(bucket, key, maximum, now):
    attempts = bucket[key]
    while attempts and attempts[0] <= now - RATE_WINDOW:
        attempts.popleft()
    if len(attempts) >= maximum:
        return False
    attempts.append(now)
    return True


@app.middleware("http")
async def simulation_session_middleware(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    now = time.monotonic()
    # client.host is the server-known peer; never trust arbitrary X-Forwarded-For.
    ip = request.client.host if request.client else "unknown"
    if not within_limit(IP_ATTEMPTS, ip, IP_LIMIT, now):
        return JSONResponse({"detail": "Too many requests"}, status_code=429,
                            headers={"Retry-After": "60"})

    session_id = request.cookies.get(SESSION_COOKIE)
    session = SESSIONS.get(session_id) if session_id else None
    is_new = session is None
    if session is None:
        if len(SESSIONS) >= MAX_SESSIONS:
            for key, item in list(SESSIONS.items()):
                if now - item.last_seen > SESSION_TTL_SECONDS and not item.lock.locked():
                    SESSIONS.pop(key, None)
                    SESSION_ATTEMPTS.pop(key, None)
        if len(SESSIONS) >= MAX_SESSIONS:
            return JSONResponse({"detail": "Server busy"}, status_code=503)
        session_id = secrets.token_urlsafe(32)
        session = new_session()
        SESSIONS[session_id] = session

    if not within_limit(SESSION_ATTEMPTS, session_id, SESSION_LIMIT, now):
        return JSONResponse({"detail": "Too many requests"}, status_code=429,
                            headers={"Retry-After": "60"})

    async with session.lock:
        session.last_seen = now
        token = SESSION_CONTEXT.set(session)
        try:
            response = await call_next(request)
        finally:
            SESSION_CONTEXT.reset(token)
    if is_new:
        response.set_cookie(SESSION_COOKIE, session_id, httponly=True,
                            secure=request.url.scheme == "https", samesite="lax",
                            max_age=SESSION_TTL_SECONDS, path="/")
    response.headers["Cache-Control"] = "no-store"
    return response


# =========================
# Lookups
# =========================

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
    "credential-execute": ("credential", "DEV001"),
    "mitm-execute": ("mitm", "CON001"),
    "dos-execute": ("dos", "DEV001"),
    "ddos-execute": ("ddos", "DEV001"),
    "malware-execute": ("malware", "DEV001"),
    "ransomware-execute": ("ransomware", "DEV001"),
}


# =========================
# Helper Functions
# =========================

def validate_attack_target(attack_name, target_id):
    from fastapi import HTTPException
    if (target_id == "CON001") != (attack_name == "mitm"):
        raise HTTPException(status_code=422, detail="Invalid target for attack")


def validate_execute_target(source_id, data):
    from fastapi import HTTPException
    if source_id not in source_methods:
        raise HTTPException(status_code=404, detail="Unknown source")
    target = data.get("target")
    if source_id == "attacker-perform":
        if target is not None:
            validate_attack_target(data.get("attack", "credential"), target)
    elif source_id in attack_sources:
        if target is not None:
            validate_attack_target(attack_sources[source_id][0], target)
    elif source_id.startswith("connection-") or source_id == "defender-secure":
        if target is not None and target != "CON001":
            raise HTTPException(status_code=422, detail="Connection target required")
    elif target == "CON001":
        raise HTTPException(status_code=422, detail="Device target required")


def get_target(target_id):
    for device in current_session().simulation.devices:
        if device.device_id == target_id:
            return device

    for connection_item in current_session().simulation.connections:
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
        for event in current_session().simulation.tracer.events
    ]

    devices = [
        device.get_data()
        for device in current_session().simulation.devices
    ]

    connections = [
        connection_item.get_data()
        for connection_item in current_session().simulation.connections
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
        attack = current_session().attacks.get(attack_name)

        if attack is None:
            return False, "Attack not found.", None

        default_target = "CON001" if attack_name == "mitm" else "DEV001"
        target = get_target(target_id or default_target)

        if target is None:
            return False, "Target not found.", None

        return True, "", current_session().simulation.perform_attack(attack, target)

    if source_id in attack_sources:
        attack_name, default_target = attack_sources[source_id]
        attack = current_session().attacks[attack_name]
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
        return True, "", current_session().simulation.inspect(device)

    if source_id == "defender-block":
        if device is None:
            return False, "Device not found.", None
        current_session().simulation.block(device)
        return True, "", None

    if source_id == "defender-unblock":
        if device is None:
            return False, "Device not found.", None
        current_session().simulation.unblock(device)
        return True, "", None

    if source_id == "defender-isolate":
        if device is None:
            return False, "Device not found.", None
        current_session().simulation.isolate(device)
        return True, "", None

    if source_id == "defender-restore":
        if device is None:
            return False, "Device not found.", None
        current_session().simulation.restore(device)
        return True, "", None

    if source_id == "defender-secure":
        if connection_target is None:
            return False, "Connection not found.", None
        current_session().simulation.secure_connection(connection_target)
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
    current_session().simulation.tracer.clear()
    return get_response()


# =========================
# Method Execution
# =========================

@app.post("/api/execute/{source_id}")
def execute_method(source_id: str, data: ExecutePayload):
    data = data.model_dump(exclude_none=True)
    validate_execute_target(source_id, data)
    current_session().simulation.tracer.clear()
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
def perform_attack(data: AttackPayload):
    data = data.model_dump()
    validate_attack_target(data["attack"], data["target"])
    current_session().simulation.tracer.clear()

    attack_name = data.get("attack")
    target_id = data.get("target")

    attack = current_session().attacks.get(attack_name)
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

    result = current_session().simulation.perform_attack(attack, target)
    return get_response(result)


# =========================
# Existing Defender Routes
# =========================

@app.post("/api/block")
def block(data: TargetPayload):
    data = data.model_dump()
    if data["target"] == "CON001":
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Device target required")
    current_session().simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    current_session().simulation.block(target)
    return get_response()


@app.post("/api/unblock")
def unblock(data: TargetPayload):
    data = data.model_dump()
    if data["target"] == "CON001":
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Device target required")
    current_session().simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    current_session().simulation.unblock(target)
    return get_response()


@app.post("/api/isolate")
def isolate(data: TargetPayload):
    data = data.model_dump()
    if data["target"] == "CON001":
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Device target required")
    current_session().simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    current_session().simulation.isolate(target)
    return get_response()


@app.post("/api/restore")
def restore(data: TargetPayload):
    data = data.model_dump()
    if data["target"] == "CON001":
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Device target required")
    current_session().simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Target not found."
        }

    current_session().simulation.restore(target)
    return get_response()


@app.post("/api/secure")
def secure_connection(data: TargetPayload):
    data = data.model_dump()
    if data["target"] != "CON001":
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Connection target required")
    current_session().simulation.tracer.clear()
    target = get_target(data.get("target"))

    if target is None:
        return {
            "success": False,
            "message": "Connection not found."
        }

    current_session().simulation.secure_connection(target)
    return get_response()


# =========================
# Reset
# =========================

@app.post("/api/reset")
def reset():
    current_session().simulation.reset()
    return get_response()


# =========================
# Frontend
# =========================

app.mount(
    "/",
    StaticFiles(directory=DOCS_DIR, html=True),
    name="frontend"
)