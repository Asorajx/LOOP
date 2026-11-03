"""Runs the LOOP web server and handles scenarios, actions, and frontend files."""
import asyncio
import secrets
import time
from collections import defaultdict, deque
from contextvars import ContextVar
from dataclasses import dataclass, field
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from engine.scenario_manager import describe, find_action, load_scenarios, run_action

app = FastAPI()
WEB_DIR = Path(__file__).resolve().parent / "web"
SCENARIOS = load_scenarios()


# =========================
# Request types
# =========================

class ActionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: str = Field(min_length=1, max_length=40)


# =========================
# Independent browser sessions
# =========================

@dataclass
class Session:
    worlds: dict
    last_seen: float
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


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


def within_limit(bucket, key, maximum, now):
    attempts = bucket[key]
    while attempts and attempts[0] <= now - RATE_WINDOW:
        attempts.popleft()
    if len(attempts) >= maximum:
        return False
    attempts.append(now)
    return True


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    if not request.url.path.startswith("/api/"):
        # Re-check page files on every load, so an update is never hidden by the browser cache.
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache"
        return response

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
        session = Session({}, now)
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


def get_scenario(scenario_id):
    scenario = SCENARIOS.get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="Unknown scenario")
    return scenario


def get_objects(scenario_id, fresh=False):
    """This browser's objects for a scenario. They persist between actions."""
    session = SESSION_CONTEXT.get()
    if fresh or scenario_id not in session.worlds:
        session.worlds[scenario_id] = SCENARIOS[scenario_id].build()
    return session.worlds[scenario_id]


# =========================
# Routes
# =========================

@app.get("/api/scenarios")
def list_scenarios():
    return [{"id": scenario_id, "title": scenario.TITLE} for scenario_id, scenario in SCENARIOS.items()]


@app.get("/api/scenarios/{scenario_id}")
def scenario_details(scenario_id: str):
    scenario = get_scenario(scenario_id)
    return describe(scenario, get_objects(scenario_id))


# Plain def: FastAPI runs it in a worker thread, and the tracer only watches that thread.
@app.post("/api/scenarios/{scenario_id}/actions/{action_id}")
def perform_action(scenario_id: str, action_id: str, data: ActionPayload):
    scenario = get_scenario(scenario_id)
    action = find_action(scenario, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Unknown action")
    if data.target not in action["targets"]:
        raise HTTPException(status_code=422, detail="Invalid target for this action")
    return run_action(scenario, get_objects(scenario_id), action, data.target)


@app.post("/api/scenarios/{scenario_id}/reset")
def reset(scenario_id: str):
    scenario = get_scenario(scenario_id)
    return describe(scenario, get_objects(scenario_id, fresh=True))["state"]


# =========================
# Frontend
# =========================

app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="frontend")
