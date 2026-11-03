"""Record what scenario code does while an action runs.

The tracer watches from outside using sys.settrace, so educational classes
never mention it. Each method call and each executed line becomes one step,
with its real file line number, the call stack, and any attribute changes.
"""

import inspect
import linecache
import os
import sys


def _normalise(path):
    return os.path.normcase(os.path.abspath(path))


class Tracer:
    def __init__(self, files, objects):
        self.files = {_normalise(path) for path in files}
        self.objects = objects
        self.labels = {id(obj): label for label, obj in objects.items()}

    # -------------------------
    # Public API
    # -------------------------

    def run(self, func, *args):
        """Call func(*args) and return (result, steps)."""
        self.steps = []
        self.stack = []
        self.current = None
        self.snapshot = self.state()
        self._known = {}

        sys.settrace(self._trace)
        try:
            result = func(*args)
        finally:
            sys.settrace(None)

        self._record_changes()
        return result, self.steps

    def state(self):
        """Every object's attributes and property values, with object references shown as labels.

        Properties are included so that state worked out from other objects (such as
        a connection that is only online while its devices are) shows up as a change.
        Code run inside the trace function isn't traced, so reading them adds no steps.
        """
        snapshot = {}
        for label, obj in self.objects.items():
            values = {name: self.value(item) for name, item in vars(obj).items()}
            for cls in type(obj).__mro__:
                for name, member in vars(cls).items():
                    if isinstance(member, property) and name not in values:
                        values[name] = self.value(getattr(obj, name))
            snapshot[label] = values
        return snapshot

    def value(self, item):
        if item is None or isinstance(item, (bool, int, float, str)):
            return item
        return self.labels.get(id(item), type(item).__name__)

    # -------------------------
    # Trace events
    # -------------------------

    def _is_scenario_file(self, path):
        if path not in self._known:
            self._known[path] = _normalise(path) in self.files
        return self._known[path]

    def _trace(self, frame, event, arg):
        """Python calls this on every function call, then on each line and return in that frame.

        Returning None for files outside the scenario stops Python reporting their lines.
        frame.f_lineno is the real file line about to run, which is how highlighting
        stays exact. Before each event, any attribute changes are credited to the line
        that was running until now (self.current).
        """
        if not self._is_scenario_file(frame.f_code.co_filename):
            return None

        if event == "call":
            self._record_changes()
            caller = self.stack[-1] if self.stack else None
            frame_info = {
                "method": frame.f_code.co_qualname,
                "object": self.value(frame.f_locals.get("self")),
                "file": os.path.basename(frame.f_code.co_filename),
                "frame": frame,
                "step": None,
            }
            route = self._route(caller, frame_info, frame)
            self.stack.append(frame_info)
            frame_info["step"] = self._add_step("call", frame_info, self._def_line(frame), route)
            self.current = frame_info["step"]

        elif event == "line":
            self._record_changes()
            frame_info = self._frame_info(frame)
            if frame_info is not None:
                frame_info["step"] = self._add_step("line", frame_info, frame.f_lineno)
                self.current = frame_info["step"]

        elif event == "return":
            self._record_changes()
            frame_info = self._frame_info(frame)
            if frame_info is not None:
                if arg is not None:
                    self.steps[frame_info["step"]]["returns"] = self.value(arg)
                self.stack.remove(frame_info)
                self.current = self.stack[-1]["step"] if self.stack else None

        return self._trace

    def _def_line(self, frame):
        """The 'def' line of the running function, skipping decorators such as @property."""
        line = frame.f_code.co_firstlineno
        while linecache.getline(frame.f_code.co_filename, line).strip().startswith("@"):
            line += 1
        return line

    def _frame_info(self, frame):
        for frame_info in reversed(self.stack):
            if frame_info["frame"] is frame:
                return frame_info
        return None

    # -------------------------
    # Steps
    # -------------------------

    def _add_step(self, kind, frame_info, line, route=None):
        step = {
            "index": len(self.steps),
            "kind": kind,
            "method": frame_info["method"],
            "object": frame_info["object"],
            "file": frame_info["file"],
            "line": line,
            "code": linecache.getline(frame_info["frame"].f_code.co_filename, line).strip(),
            "stack": [
                {"method": item["method"], "object": item["object"]}
                for item in self.stack
            ],
            "changes": [],
        }
        if route is not None:
            step["route"] = route
        self.steps.append(step)
        return step["index"]

    def _record_changes(self):
        """Compare object state with the last snapshot and credit the running line."""
        now = self.state()
        changes = []

        for label, attributes in now.items():
            before = self.snapshot.get(label, {})
            for name, new in attributes.items():
                old = before.get(name)
                if old != new:
                    changes.append({"object": label, "attribute": name, "old": old, "new": new})

        self.snapshot = now

        if changes and self.steps:
            index = self.current if self.current is not None else len(self.steps) - 1
            self.steps[index]["changes"].extend(changes)

    def _route(self, caller, callee, frame):
        """Describe how the caller reached this method: call, super() or property."""
        if caller is None:
            return {"kind": "start", "to": callee["method"], "to_object": callee["object"]}

        kind = "call"
        caller_line = linecache.getline(caller["frame"].f_code.co_filename, caller["frame"].f_lineno)

        if callee["object"] == caller["object"] and "super()" in caller_line:
            kind = "super"
        elif self._is_property(frame):
            kind = "property"

        return {
            "kind": kind,
            "from": caller["method"],
            "from_object": caller["object"],
            "to": callee["method"],
            "to_object": callee["object"],
        }

    def _is_property(self, frame):
        owner = frame.f_locals.get("self")
        class_name, _, name = frame.f_code.co_qualname.rpartition(".")
        if owner is None or not class_name:
            return False
        for cls in type(owner).__mro__:
            if cls.__name__ == class_name:
                return isinstance(inspect.getattr_static(cls, name, None), property)
        return False
