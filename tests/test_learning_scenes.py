"""Functional smoke tests for the real Python educational demonstrations."""

import pytest
from fastapi.testclient import TestClient
from attacks import Attack, CredentialAttack
from api import app

SCENES = [
    ("device-increase-risk", {"target": "DEV001"}, "NetworkDevice", "risk_level"),
    ("credential-execute", {"target": "DEV001"}, "CredentialAttack", "risk_level"),
    ("mitm-execute", {"target": "CON001"}, "Connection", "intercepted"),
    ("ddos-execute", {"target": "DEV001"}, "DDoSAttack", "traffic_level"),
    ("attacker-perform", {"target": "DEV001", "attack": "malware"}, "MalwareAttack", "risk_level"),
    ("attacker-perform", {"target": "DEV001", "attack": "credential"}, "CredentialAttack", "risk_level"),
]


@pytest.mark.parametrize("source,payload,expected_class,expected_change", SCENES)
def test_guided_lesson_runs_real_python(source, payload, expected_class, expected_change):
    with TestClient(app) as client:
        assert client.post("/api/reset").json()["success"]
        response = client.post(f"/api/execute/{source}", json=payload)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["success"]
        assert any(event["class_name"] == expected_class for event in data["events"])
        assert any(event["event_type"] == "STATE_CHANGED" and event["attribute"] == expected_change
                   for event in data["events"])


def test_class_instances_have_independent_state():
    with TestClient(app) as client:
        client.post("/api/reset")
        data = client.post("/api/execute/device-increase-risk", json={"target": "DEV001"}).json()
        devices = {item["device_id"]: item for item in data["devices"]}
        assert devices["DEV001"]["risk_level"] == 1
        assert devices["DEV002"]["risk_level"] == 0


def test_ddos_override_calls_parent_and_adds_own_behaviour():
    with TestClient(app) as client:
        client.post("/api/reset")
        data = client.post("/api/execute/ddos-execute", json={"target": "DEV001"}).json()
        started = [event["class_name"] for event in data["events"] if event["event_type"] == "METHOD_STARTED"]
        assert started.index("DDoSAttack") < started.index("DoSAttack")
        levels = [event["new_value"] for event in data["events"] if event["attribute"] == "traffic_level"]
        assert levels == ["HIGH", "CRITICAL"]
        assert data["devices"][0]["risk_level"] == 2


def test_abc_requires_concrete_execute():
    with pytest.raises(TypeError):
        Attack("Cannot instantiate abstract Attack")
    assert isinstance(CredentialAttack(), Attack)
    assert callable(CredentialAttack().execute)


def test_python_source_endpoint():
    with TestClient(app) as client:
        data = client.get("/api/source/ddos-execute").json()
        assert data["success"] and "super().execute(target)" in data["source"]
