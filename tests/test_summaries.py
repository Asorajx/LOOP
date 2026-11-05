"""Summaries follow the real result, names are filled in, and the Changed row has what it needs."""

import inspect

import pytest

from engine.scenario_manager import fill, load_scenarios, run_action

SCENARIOS = load_scenarios()


def run(scenario_id, *actions):
    """Run actions in order on one set of objects and return the last result."""
    scenario = SCENARIOS[scenario_id]
    objects = scenario.build()
    for action_id, target in actions:
        settings = next(item for item in scenario.ACTIONS if item["id"] == action_id)
        result = run_action(scenario, objects, settings, target)
    return result


# (scenario, actions leading up to the last one, expected result, expected summary story)
OUTCOMES = [
    ("library", [("borrow", "BOOK001")], True,
     "Member A successfully borrows Book A. The other book isn't affected."),
    ("library", [("borrow", "BOOK001"), ("borrow", "BOOK001")], False,
     "Member A cannot borrow Book A because it is already borrowed."),
    ("library", [("borrow", "BOOK001"), ("return", "BOOK001")], True,
     "Member A returns Book A, and it is available again."),
    ("library", [("return", "BOOK001")], False,
     "Member A cannot return Book A because Member A has not borrowed it."),
    ("library", [("borrow", "BOOK002"), ("renew", "BOOK002")], True,
     "Member A renews the loan of Book B. It has now been renewed once."),
    ("library", [("renew", "BOOK002")], False,
     "Member A cannot renew Book B because it isn't borrowed."),
    ("library", [("borrow", "BOOK001"), ("renew", "BOOK001"), ("renew", "BOOK001")], False,
     "Member A cannot renew Book A because the loan has already been renewed once."),
    ("library", [("check", "BOOK001")], "Available",
     "City Library reports that Book A is available."),
    ("library", [("borrow", "BOOK001"), ("check", "BOOK001")], "On loan",
     "City Library reports that Book A is on loan."),
    ("cybersecurity", [("malware", "DEV001")], True,
     "Device A is infected. The other device keeps its own state."),
    ("cybersecurity", [("isolate", "DEV001"), ("malware", "DEV001")], False,
     "Device A is offline, so the malware never reached it."),
    ("cybersecurity", [("ransomware", "DEV002")], True,
     "Device B is infected and its files are locked."),
    ("cybersecurity", [("isolate", "DEV002"), ("ransomware", "DEV002")], False,
     "Device B is offline, so the ransomware never reached it."),
    ("cybersecurity", [("intercept", "CON001")], True,
     "Messages on the connection are now being intercepted."),
    ("cybersecurity", [("isolate", "DEV002"), ("intercept", "CON001")], False,
     "The connection is offline because at least one device is disconnected, so the attack never reached it."),
    ("cybersecurity", [("isolate", "DEV001")], None,
     "Device A is offline, so attacks can't reach it. The connection is offline too."),
    ("smart_home", [("set_temperature", "THERMO001")], False,
     "Home Owner cannot change Hallway Thermostat's temperature because it is switched off."),
    ("smart_home", [("switch_on", "THERMO001"), ("set_temperature", "THERMO001")], True,
     "Hallway Thermostat is set to 23°C."),
    ("smart_home", [("set_brightness", "LIGHT001")], False,
     "Home Owner cannot dim Living Room Light because it is switched off."),
    ("smart_home", [("switch_on", "LIGHT001"), ("set_brightness", "LIGHT001")], True,
     "Living Room Light is dimmed to 50%."),
]


@pytest.mark.parametrize("scenario_id,actions,expected,story", OUTCOMES)
def test_summary_matches_the_real_result(scenario_id, actions, expected, story):
    result = run(scenario_id, *actions)
    assert result["result"] == expected
    assert result["outcome"] == ("failure" if expected is False else "success")
    assert result["summary"]["story"] == story
    assert result["summary"]["concept"] and result["summary"]["lesson"]


def test_failed_actions_change_nothing_and_say_so():
    for scenario_id, actions, expected, _ in OUTCOMES:
        if expected is False:
            result = run(scenario_id, *actions)
            assert result["before"] == result["after"]
            assert "cannot" in result["summary"]["story"] or "never reached" in result["summary"]["story"]


def every_run():
    """Every action and target, on fresh objects and after every other action has run once."""
    for scenario_id, scenario in SCENARIOS.items():
        for first in scenario.ACTIONS:
            for first_target in first["targets"]:
                for action in scenario.ACTIONS:
                    for target in action["targets"]:
                        objects = scenario.build()
                        run_action(scenario, objects, first, first_target)
                        yield scenario, run_action(scenario, objects, action, target)


def test_no_placeholder_is_left_unfilled():
    for scenario, result in every_run():
        texts = [result["story"], *result["summary"].values()]
        for step in result["steps"]:
            texts += [value for value in (step["explain"] or {}).values()]
        for text in texts:
            assert "{" not in text and "}" not in text, (scenario.TITLE, text)


def test_every_action_has_a_summary_for_its_real_outcome():
    for scenario, result in every_run():
        assert result["summary"].get("story"), (scenario.TITLE, result["call"], result["result"])


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_no_object_shares_its_class_name(scenario_id):
    """An object called "Thermostat" of class Thermostat blurs the difference between the two."""
    for obj in SCENARIOS[scenario_id].build().values():
        if hasattr(obj, "name"):
            class_words = {type(obj).__name__.lower()}
            class_words |= {cls.__name__.lower() for cls in inspect.getmro(type(obj))}
            spaced = obj.name.lower().replace(" ", "")
            assert spaced not in class_words, f"{obj.name!r} matches its class name"


def test_renamed_objects_appear_in_the_terminal_text():
    result = run("smart_home", ("switch_on", "THERMO001"))
    assert result["story"] == "Home Owner wants to switch on Hallway Thermostat."
    assert result["steps"][1]["explain"]["story"] == "Home Owner asks Main Hub to switch on Hallway Thermostat."
    assert run("library", ("borrow", "BOOK001"))["steps"][1]["explain"]["story"] == (
        "Member A asks City Library to lend Book A.")
    assert run("cybersecurity", ("isolate", "DEV001"))["story"] == (
        "Device Owner disconnects Device A so attacks can't reach it.")


def test_changes_mark_object_references_and_properties():
    borrowed = next(step for step in run("library", ("borrow", "BOOK001"))["steps"]
                    if step["code"] == "self.borrowed_by = member")
    changes = {change["attribute"]: change for change in borrowed["changes"]}
    assert changes["borrowed_by"]["new"] == "member" and changes["borrowed_by"]["new_is_object"] is True
    assert changes["borrowed_by"]["old_is_object"] is False and changes["borrowed_by"]["property"] is False
    assert changes["available"]["property"] is True and changes["available"]["new"] is False

    returned = next(step for step in run("library", ("borrow", "BOOK001"), ("return", "BOOK001"))["steps"]
                    if step["code"] == "self.borrowed_by = None")
    change = next(change for change in returned["changes"] if change["attribute"] == "borrowed_by")
    assert change["old_is_object"] is True and change["new_is_object"] is False

    disconnect = next(step for step in run("cybersecurity", ("isolate", "DEV001"))["steps"]
                      if step["code"] == "self.online = False")
    kinds = {(change["object"], change["property"]) for change in disconnect["changes"]}
    assert kinds == {("DEV001", False), ("CON001", True)}


def test_abstraction_is_explained_on_the_malware_action():
    step = run("cybersecurity", ("malware", "DEV001"))["steps"][3]
    assert step["method"] == "MalwareAttack.execute" and step["kind"] == "call"
    assert step["explain"]["concept"] == "abstraction"
    assert "abstract" in step["explain"]["detail"] and "MalwareAttack" in step["explain"]["detail"]


def test_renew_explanation_matches_the_condition():
    step = next(step for step in run("library", ("renew", "BOOK001"))["steps"]
                if step["code"].startswith("if self.borrowed_by is not member"))
    assert "is not the borrower" in step["explain"]["code"]


def test_concept_detail_never_names_the_target_as_the_other_object():
    for target in ("BOOK001", "BOOK002"):
        result = run("library", ("borrow", target), ("renew", target))
        detail = next(step for step in result["steps"] if step["code"] == "self.renewals += 1")["explain"]["detail"]
        name = SCENARIOS["library"].build()[target].name
        assert detail.count(name) == 1


def test_fill_capitalises_names_that_start_a_sentence():
    names = {"CON001": "the connection"}
    assert fill("{CON001} is offline.", names, "x", "y") == "The connection is offline."
    assert fill("A is down. {CON001} is too.", names, "x", "y") == "A is down. The connection is too."
    assert fill("Messages on {CON001}.", names, "x", "y") == "Messages on the connection."
    assert fill("Keep {unknown} as it is.", names, "x", "y") == "Keep {unknown} as it is."
