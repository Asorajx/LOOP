"""Checks that apply to every scenario, so new scenarios are tested automatically."""

import inspect
from pathlib import Path

import pytest

from engine.scenario_manager import all_classes, describe, load_scenarios, run_action

SCENARIOS = load_scenarios()
ACTIONS = [
    (scenario_id, action["id"], target)
    for scenario_id, scenario in SCENARIOS.items()
    for action in scenario.ACTIONS
    for target in action["targets"]
]


def method_source(scenario, qualname):
    class_name, method_name = qualname.split(".")
    cls = next(cls for cls in all_classes(scenario) if cls.__name__ == class_name)
    member = inspect.getattr_static(cls, method_name)
    function = member.fget if isinstance(member, property) else member
    return [line.strip() for line in inspect.getsourcelines(function)[0]]


@pytest.mark.parametrize("scenario_id,action_id,target", ACTIONS)
def test_every_action_runs_and_lines_match_the_real_files(scenario_id, action_id, target):
    scenario = SCENARIOS[scenario_id]
    objects = scenario.build()
    action = next(item for item in scenario.ACTIONS if item["id"] == action_id)
    files = describe(scenario, objects)["files"]

    result = run_action(scenario, objects, action, target)

    assert result["steps"], "an action should execute scenario code"
    for step in result["steps"]:
        assert files[step["file"]][step["line"] - 1].strip() == step["code"]


@pytest.mark.parametrize("scenario_id,action_id,target", ACTIONS)
def test_clicked_method_runs_inside_the_full_action(scenario_id, action_id, target):
    """Clicking an action's def line must run the whole path, including that method."""
    scenario = SCENARIOS[scenario_id]
    action = next(item for item in scenario.ACTIONS if item["id"] == action_id)

    result = run_action(scenario, scenario.build(), action, target)

    methods = [step["method"] for step in result["steps"]]
    assert action["method"] in methods
    assert methods[0] == f"{type(scenario.build()[action['call'][0]]).__name__}.{action['call'][1]}"


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_explanations_point_at_real_methods_and_lines(scenario_id):
    scenario = SCENARIOS[scenario_id]
    for qualname, entries in scenario.story.EXPLAIN.items():
        lines = method_source(scenario, qualname)
        for key in entries:
            if key not in ("call", "super", "property"):
                assert key in lines, f"{qualname}: {key!r} is not a line in the real source"


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_every_action_has_a_story_and_summary(scenario_id):
    scenario = SCENARIOS[scenario_id]
    action_ids = {action["id"] for action in scenario.ACTIONS}
    assert action_ids == set(scenario.story.ACTION_STORIES)
    assert action_ids == set(scenario.story.ACTION_SUMMARIES)


# Must match the concept ids in web/js/concepts.js.
CONCEPT_IDS = {"classes", "attributes", "methods", "inheritance", "encapsulation",
               "polymorphism", "abstraction", "relationships"}


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_concepts_are_known(scenario_id):
    story = SCENARIOS[scenario_id].story
    entries = [entry for lines in story.EXPLAIN.values() for entry in lines.values()]
    entries += list(story.ACTION_SUMMARIES.values()) + [getattr(story, "FALSE_SUMMARY", {})]
    for entry in entries:
        assert entry.get("concept", "methods") in CONCEPT_IDS


@pytest.mark.parametrize("scenario_id", SCENARIOS)
def test_educational_files_contain_no_tracing_code(scenario_id):
    scenario = SCENARIOS[scenario_id]
    for path in {inspect.getsourcefile(cls) for cls in all_classes(scenario)}:
        text = Path(path).read_text(encoding="utf-8")
        assert "tracer" not in text.lower() and "engine" not in text
