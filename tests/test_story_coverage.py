"""Every terminal step should have a plain Story and Code explanation."""

import pytest

from engine.scenario_manager import load_scenarios, run_action


SCENARIOS = load_scenarios()


def action(scenario, objects, action_id, target):
    settings = next(item for item in scenario.ACTIONS if item["id"] == action_id)
    return run_action(scenario, objects, settings, target)


def test_all_actions_and_targets_have_story_and_code_for_every_step():
    for scenario in SCENARIOS.values():
        for settings in scenario.ACTIONS:
            for target in settings["targets"]:
                result = action(scenario, scenario.build(), settings["id"], target)
                for step in result["steps"]:
                    explain = step["explain"]
                    assert explain is not None, (scenario.TITLE, settings["id"], step)
                    assert explain.get("story"), (scenario.TITLE, settings["id"], step)
                    assert explain.get("code"), (scenario.TITLE, settings["id"], step)


@pytest.mark.parametrize("scenario_id,actions", [
    ("library", [("borrow", "BOOK001"), ("check", "BOOK001"),
                 ("borrow", "BOOK001"), ("renew", "BOOK001"),
                 ("renew", "BOOK001"), ("return", "BOOK001"),
                 ("return", "BOOK001")]),
    ("cybersecurity", [("malware", "DEV001"), ("ransomware", "DEV001"),
                       ("intercept", "CON001"), ("isolate", "DEV001"),
                       ("intercept", "CON001"), ("ransomware", "DEV001"),
                       ("recover", "DEV001"), ("secure", "CON001")]),
    ("smart_home", [("set_brightness", "LIGHT001"), ("switch_on", "LIGHT001"),
                    ("set_brightness", "LIGHT001"), ("switch_off", "LIGHT001"),
                    ("set_temperature", "THERMO001"), ("switch_on", "THERMO001"),
                    ("set_temperature", "THERMO001"), ("switch_off", "THERMO001"),
                    ("switch_on", "FAN001"), ("switch_off", "FAN001"),
                    ("lock", "DOOR001"), ("unlock", "DOOR001")]),
])
def test_explanations_also_cover_success_and_failure_paths(scenario_id, actions):
    scenario = SCENARIOS[scenario_id]
    objects = scenario.build()
    for action_id, target in actions:
        result = action(scenario, objects, action_id, target)
        for step in result["steps"]:
            assert step["explain"] and step["explain"].get("story")
            assert step["explain"].get("code")


def test_library_availability_story_changes_with_result():
    scenario = SCENARIOS["library"]
    objects = scenario.build()
    borrow = action(scenario, objects, "borrow", "BOOK001")
    first_check = next(step for step in borrow["steps"] if step["method"] == "Book.available" and step["kind"] == "line")
    assert first_check["explain"]["story"] == "Book A is not borrowed, so it is available."

    later = action(scenario, objects, "check", "BOOK001")
    later_check = next(step for step in later["steps"] if step["method"] == "Book.available" and step["kind"] == "line")
    assert later_check["explain"]["story"] == "Book A is already borrowed, so it is unavailable."


def test_only_oop_concepts_are_shown():
    oop_ids = {"classes", "attributes", "methods", "properties", "inheritance", "encapsulation", "polymorphism", "abstraction", "relationships"}
    for scenario in SCENARIOS.values():
        for steps in scenario.story.EXPLAIN.values():
            for explanation in steps.values():
                if "concept" in explanation:
                    assert explanation["concept"] in oop_ids
