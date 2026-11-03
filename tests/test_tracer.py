"""The tracer must report what Python really did."""

import engine.scenario_manager as scenario_manager
from engine.scenario_manager import discover_routes, find_action, load_scenarios, run_action

cyber = load_scenarios()["cybersecurity"]


def run(action_id, target, objects=None):
    return run_action(cyber, objects or cyber.build(), find_action(cyber, action_id), target)


def test_super_call_runs_parent_on_the_same_object():
    result = run("ransomware", "DEV001")
    parent = next(step for step in result["steps"]
                  if step["kind"] == "call" and step["method"] == "MalwareAttack.execute")

    assert parent["route"] == {"kind": "super", "from": "RansomwareAttack.execute", "from_object": "ransomware",
                               "to": "MalwareAttack.execute", "to_object": "ransomware"}
    assert [item["method"] for item in parent["stack"]] == [
        "Attacker.launch", "RansomwareAttack.execute", "MalwareAttack.execute"]


def test_state_changes_are_credited_to_the_line_that_made_them():
    result = run("ransomware", "DEV001")
    changes = [(step["code"], change["object"], change["attribute"], change["old"], change["new"])
               for step in result["steps"] for change in step["changes"]]

    assert changes == [
        ("self.infected = True", "DEV001", "infected", False, True),
        ("self.files_locked = True", "DEV001", "files_locked", False, True),
    ]


def test_property_changes_show_object_relationships():
    """Disconnecting a device also changes the connection that holds it."""
    result = run("isolate", "DEV001")
    changes = [(step["code"], change["object"], change["attribute"], change["new"])
               for step in result["steps"] for change in step["changes"]]

    assert ("self.online = False", "DEV001", "online", False) in changes
    assert ("self.online = False", "CON001", "online", False) in changes


def test_property_reads_are_traced_as_properties():
    result = run("intercept", "CON001")
    step = next(step for step in result["steps"] if step["method"] == "Connection.online")
    assert step["route"]["kind"] == "property"
    assert step["code"] == "def online(self):"


def test_return_values_are_recorded():
    result = run("malware", "DEV001")
    assert result["steps"][-1]["code"] == "return True"
    assert result["steps"][-1]["returns"] is True


def test_only_scenario_files_are_traced():
    result = run("ransomware", "DEV001")
    assert {step["file"] for step in result["steps"]} == {"attacks.py", "devices.py"}


def test_route_discovery_finds_real_calls():
    routes = {(route["from"], route["to"], route["kind"]) for route in discover_routes(cyber)}

    assert ("Attacker.launch", "RansomwareAttack.execute", "call") in routes
    assert ("RansomwareAttack.execute", "MalwareAttack.execute", "super") in routes
    assert ("MalwareAttack.execute", "Device.infect", "call") in routes
    assert ("Attacker.launch", "Connection.online", "property") in routes
    assert ("Victim.secure", "Connection.secure", "call") in routes


def test_route_discovery_does_not_touch_existing_objects():
    objects = cyber.build()
    run("malware", "DEV001", objects)
    scenario_manager._discovered.clear()  # force a fresh discovery run

    discover_routes(cyber)

    assert objects["DEV001"].infected is True
    assert objects["DEV002"].infected is False
