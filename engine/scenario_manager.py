"""Find scenarios, describe them for the browser, and run their actions.

A scenario is a folder in scenarios/ with a scenario.py that defines:
    TITLE    the tab name
    ORDER    optional tab position (lower first); scenarios without one come last
    PANELS   list of (panel title, [classes]), two or three panels
    ACTIONS  list of action dicts (see scenarios/cybersecurity/scenario.py)
    STATUS   optional {attribute: settings} drawn as status icons
    build()  returns {label: object} for a fresh simulation; an object's
             name attribute, if it has one, is used as its display name
and a story.py that defines ACTION_STORIES, ACTION_SUMMARIES and EXPLAIN.

Each ACTION_SUMMARIES entry has a "success" summary and, for actions that can
return False, a "failure" summary. The one shown depends on the real result.
Either can instead be a list of summaries with "when" conditions on the target's
final state, such as {"when": {"available": True}, ...}; the first match is shown.

Story text can use {target} (the chosen target), {object} (the object running
the step), {result} (the action's return value) and {label} for any object
from build(), such as {member}. Each is replaced by that object's display name.
"""

import importlib
import pkgutil
import re

import scenarios as scenario_package
from engine.source import describe_class, read_files, source_files
from engine.tracer import Tracer

TARGET = "<target>"


def load_scenarios():
    """Every scenario folder, in tab order: by ORDER, then by folder name."""
    found = {}
    for info in pkgutil.iter_modules(scenario_package.__path__):
        if info.ispkg:
            found[info.name] = importlib.import_module(f"scenarios.{info.name}.scenario")
    return dict(sorted(found.items(), key=lambda item: (getattr(item[1], "ORDER", float("inf")), item[0])))


def all_classes(scenario):
    return [cls for _, classes in scenario.PANELS for cls in classes]


def describe(scenario, objects):
    """Everything the browser needs to draw a scenario."""
    classes = all_classes(scenario)
    return {
        "title": scenario.TITLE,
        "panels": [
            {"title": title, "classes": [describe_class(cls, classes, objects) for cls in panel_classes]}
            for title, panel_classes in scenario.PANELS
        ],
        "actions": [
            {key: action[key] for key in ("id", "method", "targets")}
            for action in scenario.ACTIONS
        ],
        "status": getattr(scenario, "STATUS", {}),
        "names": display_names(objects),
        "files": read_files(source_files(classes)),
        "routes": discover_routes(scenario),
        "state": Tracer([], objects).state(),
    }


def display_names(objects):
    """Friendly names such as "Device A", taken from each object's name attribute."""
    return {label: str(getattr(obj, "name", label)) for label, obj in objects.items()}


_discovered = {}


def discover_routes(scenario):
    """Which methods call which, found by running every action once on fresh objects.

    The objects come from a new build(), so no user's state is touched. Routes that
    only appear in other states are added by the browser when a real run finds them.
    """
    if scenario.__name__ not in _discovered:
        routes = {}
        for action in scenario.ACTIONS:
            for target in action["targets"]:
                for step in run_action(scenario, scenario.build(), action, target)["steps"]:
                    route = step.get("route", {})
                    if route.get("from"):
                        routes[(route["from"], route["to"])] = {
                            key: route[key] for key in ("from", "to", "kind")
                        }
        _discovered[scenario.__name__] = list(routes.values())
    return _discovered[scenario.__name__]


def find_action(scenario, action_id):
    return next((action for action in scenario.ACTIONS if action["id"] == action_id), None)


def run_action(scenario, objects, action, target):
    """Run one action under the tracer and explain each step."""
    name, method, *args = action["call"]
    values = [objects[target] if arg == TARGET else objects.get(arg, arg) if isinstance(arg, str) else arg
              for arg in args]
    shown = [target if arg == TARGET else str(arg) for arg in args]

    tracer = Tracer(source_files(all_classes(scenario)), objects)
    before = tracer.state()
    result, steps = tracer.run(getattr(objects[name], method), *values)

    names = display_names(objects)
    for step in steps:
        step["explain"] = explain_step(scenario, step, names, names[target],
                                       names.get(step["object"], step["object"]))

    # The summary follows what really happened: False means the action was refused.
    outcome = "failure" if result is False else "success"
    after = tracer.state()
    summary = pick_summary(scenario.story.ACTION_SUMMARIES.get(action["id"], {}).get(outcome), after[target])

    return {
        "call": f"{name}.{method}({', '.join(shown)})",
        "story": fill(scenario.story.ACTION_STORIES.get(action["id"], ""), names, names[target], names[name]),
        "before": before,
        "steps": steps,
        "after": after,
        "result": tracer.value(result),
        "outcome": outcome,
        "summary": {key: fill(value, names, names[target], names[name], result)
                    for key, value in summary.items()},
    }


def pick_summary(options, target_state):
    """The first summary whose "when" values all match the target's final state."""
    for option in options if isinstance(options, list) else [options or {}]:
        if all(target_state.get(key) == value for key, value in option.get("when", {}).items()):
            return {key: value for key, value in option.items() if key != "when"}
    return {}


def explain_step(scenario, step, names, target_name, object_name):
    """Find the hand-written explanation for this call or line, if there is one."""
    lines = scenario.story.EXPLAIN.get(step["method"], {})
    if step["kind"] == "call":
        kind = step["route"]["kind"]
        text = lines.get(kind) if kind in ("super", "property") else None
        text = text or lines.get("call")
    else:
        text = lines.get(step["code"])

    if not text:
        return None

    # A line that returns True or False can have a story and code explanation for each
    # result. The tracer records the return value on the last line a method runs.
    selected = dict(text)
    if isinstance(step.get("returns"), bool):
        outcome = "true" if step["returns"] else "false"
        for field in ("story", "code"):
            if f"{field}_{outcome}" in selected:
                selected[field] = selected[f"{field}_{outcome}"]
    for field in ("story_true", "story_false", "code_true", "code_false"):
        selected.pop(field, None)
    return {key: fill(value, names, target_name, object_name) for key, value in selected.items()}


def fill(text, names, target, obj, result=None):
    """Replace {target}, {object}, {result} and object labels such as {member} with display names."""
    if not isinstance(text, str):
        return text
    values = {**names, "target": target, "object": obj, "result": result}

    def name(match):
        if match.group(2) not in values:
            return match.group(0)
        value = str(values[match.group(2)])
        # A name such as "the connection" that starts a sentence needs a capital letter.
        starts_sentence = match.group(1) is not None
        return (match.group(1) or "") + (value[:1].upper() + value[1:] if starts_sentence else value)

    return re.sub(r"(^|[.!?]\s+)?\{(\w+)\}", name, text)
