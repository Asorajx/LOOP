"""Behaviour of the cybersecurity scenario and the HTTP API."""

import pytest
from fastapi.testclient import TestClient

from api import app
from scenarios.cybersecurity.attacks import Attack
from scenarios.cybersecurity.devices import Device

URL = "/api/scenarios/cybersecurity"


def act(client, action, target):
    response = client.post(f"{URL}/actions/{action}", json={"target": target})
    assert response.status_code == 200, response.text
    return response.json()


def test_objects_of_one_class_keep_separate_state():
    device_a, device_b = Device("A"), Device("B")
    device_a.infect()
    assert device_a.infected is True
    assert device_b.infected is False


def test_state_persists_between_actions_until_reset():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "malware", "DEV001")
        after = act(client, "ransomware", "DEV002")["after"]
        assert after["DEV001"]["infected"] is True and after["DEV001"]["files_locked"] is False
        assert after["DEV002"]["infected"] is True and after["DEV002"]["files_locked"] is True

        state = client.post(f"{URL}/reset").json()
        assert state["DEV001"]["infected"] is False


def test_isolated_device_blocks_attacks():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "isolate", "DEV001")
        result = act(client, "malware", "DEV001")
        assert result["result"] is False
        assert "Device A is offline" in result["summary"]["story"]
        assert result["after"]["DEV001"]["infected"] is False
        assert "MalwareAttack.execute" not in {step["method"] for step in result["steps"]}


def test_isolating_a_device_takes_the_connection_offline():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        assert act(client, "intercept", "CON001")["after"]["CON001"]["intercepted"] is True
        act(client, "secure", "CON001")

        after = act(client, "isolate", "DEV002")["after"]
        assert after["CON001"]["online"] is False

        result = act(client, "intercept", "CON001")
        assert result["result"] is False
        assert result["after"]["CON001"]["intercepted"] is False


def test_secure_calls_the_connections_own_method():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "intercept", "CON001")
        result = act(client, "secure", "CON001")
        assert result["after"]["CON001"]["intercepted"] is False
        assert [step["method"] for step in result["steps"] if step["kind"] == "call"] == [
            "Victim.secure", "Connection.secure"]


def test_recover_resets_the_device():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "ransomware", "DEV001")
        act(client, "isolate", "DEV001")
        after = act(client, "recover", "DEV001")["after"]["DEV001"]
        assert after == {"name": "Device A", "online": True, "infected": False, "files_locked": False}


def test_invalid_requests_are_rejected():
    with TestClient(app) as client:
        assert client.post(f"{URL}/actions/malware", json={"target": "CON001"}).status_code == 422
        assert client.post(f"{URL}/actions/ddos", json={"target": "DEV001"}).status_code == 404
        assert client.get("/api/scenarios/unknown").status_code == 404


def test_browser_sessions_are_independent():
    with TestClient(app) as first, TestClient(app) as second:
        act(first, "malware", "DEV001")
        assert second.get(URL).json()["state"]["DEV001"]["infected"] is False


def test_abstract_attack_cannot_be_created():
    with pytest.raises(TypeError):
        Attack()
