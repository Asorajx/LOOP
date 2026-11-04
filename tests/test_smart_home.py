"""Behaviour of the smart home scenario."""

from fastapi.testclient import TestClient

from api import app
from engine.scenario_manager import describe, load_scenarios
from scenarios.smart_home.devices import DoorLock, SmartDevice

URL = "/api/scenarios/smart_home"


def act(client, action, target):
    response = client.post(f"{URL}/actions/{action}", json={"target": target})
    assert response.status_code == 200, response.text
    return response.json()


def call_steps(result):
    return [step for step in result["steps"] if step["kind"] == "call"]


def test_three_actor_columns_and_six_actions():
    smart_home = load_scenarios()["smart_home"]
    data = describe(smart_home, smart_home.build())
    assert [panel["title"] for panel in data["panels"]] == ["Resident", "Home Hub", "Devices"]
    assert len(data["actions"]) == 6


def test_devices_start_off_and_the_door_locked():
    with TestClient(app) as client:
        state = client.post(f"{URL}/reset").json()
        assert state["LIGHT001"]["is_on"] is False and state["LIGHT001"]["brightness"] == 0
        assert state["FAN001"]["is_on"] is False and state["FAN001"]["speed"] == 0
        assert state["THERMO001"]["is_on"] is False and state["THERMO001"]["temperature"] == 22
        assert state["DOOR001"]["locked"] is True


def test_settings_are_refused_while_a_device_is_off():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        temperature = act(client, "set_temperature", "THERMO001")
        assert temperature["result"] is False and temperature["after"]["THERMO001"]["temperature"] == 22
        assert temperature["summary"]["story"] == "Thermostat is switched off, so nothing changed."
        brightness = act(client, "set_brightness", "LIGHT001")
        assert brightness["result"] is False and brightness["after"]["LIGHT001"]["brightness"] == 0


def test_light_switches_on_through_the_hub_and_super():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        result = act(client, "switch_on", "LIGHT001")
        steps = call_steps(result)
        assert [step["method"] for step in steps] == [
            "Resident.switch_on", "HomeHub.activate", "Light.turn_on", "SmartDevice.turn_on"]
        assert steps[-1]["route"]["kind"] == "super"
        assert "called super()" in steps[-1]["explain"]["code"]
        assert "own turn_on()" in steps[2]["explain"]["code"]
        assert result["after"]["LIGHT001"]["is_on"] is True and result["after"]["LIGHT001"]["brightness"] == 100

        dimmed = act(client, "set_brightness", "LIGHT001")
        assert dimmed["result"] is True and dimmed["after"]["LIGHT001"]["brightness"] == 50


def test_thermostat_uses_the_inherited_turn_on():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        steps = call_steps(act(client, "switch_on", "THERMO001"))
        assert [step["method"] for step in steps] == [
            "Resident.switch_on", "HomeHub.activate", "SmartDevice.turn_on"]
        assert steps[-1]["route"]["kind"] == "call"
        assert "inherits" in steps[-1]["explain"]["code"] and "super()" not in steps[-1]["explain"]["code"]

        result = act(client, "set_temperature", "THERMO001")
        assert result["result"] is True and result["after"]["THERMO001"]["temperature"] == 23


def test_fan_switches_on_and_off():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        assert act(client, "switch_on", "FAN001")["after"]["FAN001"] | {"name": None} == {
            "name": None, "is_on": True, "speed": 1}
        result = act(client, "switch_off", "FAN001")
        assert [step["method"] for step in call_steps(result)][-2:] == ["Fan.turn_off", "SmartDevice.turn_off"]
        assert result["after"]["FAN001"]["is_on"] is False and result["after"]["FAN001"]["speed"] == 0


def test_door_unlocks_and_locks_without_touching_other_devices():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        act(client, "switch_on", "LIGHT001")
        unlocked = act(client, "unlock", "DOOR001")
        assert unlocked["after"]["DOOR001"]["locked"] is False
        assert unlocked["after"]["LIGHT001"] == unlocked["before"]["LIGHT001"]
        assert act(client, "lock", "DOOR001")["after"]["DOOR001"]["locked"] is True


def test_switching_one_device_leaves_the_others_alone():
    with TestClient(app) as client:
        client.post(f"{URL}/reset")
        result = act(client, "switch_on", "LIGHT001")
        for label in ("FAN001", "THERMO001", "DOOR001"):
            assert result["after"][label] == result["before"][label]


def test_door_lock_is_not_a_smart_device():
    assert not isinstance(DoorLock("Front Door"), SmartDevice)


def test_scenarios_are_listed_in_tab_order():
    with TestClient(app) as client:
        assert [item["id"] for item in client.get("/api/scenarios").json()] == [
            "cybersecurity", "library", "smart_home"]
