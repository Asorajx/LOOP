"""Read genuine source code and line numbers for the scenario classes."""

import inspect
from abc import ABC
from pathlib import Path


def source_files(classes):
    """Absolute paths of the files that define the given classes."""
    return sorted({inspect.getsourcefile(cls) for cls in classes})


def read_files(paths):
    """Full file text, line by line, keyed by file name."""
    return {
        Path(path).name: Path(path).read_text(encoding="utf-8").splitlines()
        for path in paths
    }


def describe_class(cls, classes, objects):
    """Class name, bases, line range, methods and instances for one class."""
    lines, start = inspect.getsourcelines(cls)
    methods = []

    for name, member in cls.__dict__.items():
        function = member.fget if isinstance(member, property) else member
        if not inspect.isfunction(function):
            continue
        method_lines, method_start = inspect.getsourcelines(function)
        methods.append({
            "name": name,
            "id": f"{cls.__name__}.{name}",
            "start": method_start,
            "end": method_start + len(method_lines) - 1,
            "property": isinstance(member, property),
            "abstract": getattr(function, "__isabstractmethod__", False),
        })

    return {
        "name": cls.__name__,
        "bases": [base.__name__ for base in cls.__bases__ if base in classes],
        "abstract": ABC in cls.__bases__ or inspect.isabstract(cls),
        "file": Path(inspect.getsourcefile(cls)).name,
        "start": start,
        "end": start + len(lines) - 1,
        "methods": methods,
        "objects": [label for label, obj in objects.items() if type(obj) is cls],
    }
