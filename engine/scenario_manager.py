"""Find scenarios, describe them for the browser, and run their actions.

A scenario is a folder in scenarios/ with a scenario.py that defines:
    TITLE    the tab name
    ORDER    optional tab position (lower first); scenarios without one come last
    PANELS   list of (panel title, [classes]), two or three panels
    ACTIONS  list of action dicts (see scenarios/cybersecurity/scenario.py)
    STATUS   optional {attribute: settings} drawn as status icons
    build()  returns {label: object} for a fresh simulation; an object's
             name attribute, if it has one, is used as its display name
and a story.py that defines ACTION_STORIES, ACTION_SUMMARIES and EXPLAIN
(and optionally FALSE_SUMMARY, used when an action returns False).
"""

import importlib
import pkgutil

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
        step["explain"] = explain_step(scenario, step, names[target], names.get(step["object"], step["object"]))

    summary = scenario.story.ACTION_SUMMARIES.get(action["id"])
    if result is False and hasattr(scenario.story, "FALSE_SUMMARY"):
        summary = scenario.story.FALSE_SUMMARY

    return {
        "call": f"{name}.{method}({', '.join(shown)})",
        "story": fill(scenario.story.ACTION_STORIES.get(action["id"], ""), names[target], names[name]),
        "before": before,
        "steps": steps,
        "after": tracer.state(),
        "result": tracer.value(result),
        "summary": {key: fill(value, names[target], names[name], result)
                    for key, value in (summary or {}).items()},
    }


def explain_step(scenario, step, target_name, object_name):
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
    return {key: fill(value, target_name, object_name) for key, value in text.items()}


def fill(text, target, obj, result=None):
    if not isinstance(text, str):
        return text
    starts_with_name = text.startswith(("{target}", "{object}"))
    text = (text.replace("{target}", str(target))
                .replace("{object}", str(obj))
                .replace("{result}", str(result)))
    # A sentence that starts with a name such as "the connection" needs a capital letter.
    return text[:1].upper() + text[1:] if starts_with_name else text
