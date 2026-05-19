"""
Parameter system for the rig framework.

Defines `Main`, a lightweight base class that owns a typed parameter
dictionary. Both `Guide` (per-component) and `RigGuide` (top-level rig
container) inherit from it so they share the same parameter API
(add/get/set/remove + serialization-ready type info).

This module creates no Maya nodes — it is pure data.
"""


class Main(object):
    """
    Base class providing a typed parameter dictionary.

    A Main holds a `values` dict mapping parameter name to
    `{"value": Any, "type": str}`. The type tag mirrors Maya attribute
    types (`"string"`, `"long"`, `"float"`, etc.) so that subclasses like
    Guide can later create matching attributes on scene nodes from the
    same parameter declaration.

    Subclass contract:
        Override `_define_parameters()` to register component-specific
        parameters via `add_parameter()`.

    Key attributes:
        values: parameter dict, keyed by name. Each entry stores both the
            current value and a type tag used for Maya attribute creation
            and serialization.
    """

    def __init__(self):
        self.values = {}
        self._define_parameters()

    def add_parameter(self, name, value=None, at_type="string"):
        """Register a parameter. No-op with a warning if `name` already exists."""
        if name in self.values:
            print(f"{name} is already in parameters.")
            return
        self.values[name] = {"value": value, "type": at_type}

    def remove_parameter(self, name):
        """Remove a parameter. Warn if it doesn't exist."""
        if name in self.values:
            self.values.pop(name, None)
        else:
            print(f"{name} is not in parameters.")

    def get_parameter_value(self, name):
        """Return the parameter's value, or None and warn if missing."""
        try:
            return self.values[name]["value"]
        except KeyError:
            print(f"{name} is not in parameters.")

    def set_parameter_value(self, name, value):
        """Set the parameter's value. Warn if `name` doesn't exist."""
        if name in self.values:
            self.values[name]["value"] = value
        else:
            print(f"{name} is not in parameters.")

    def get_parameter_type(self, name):
        """Return the parameter's type tag (e.g. 'string', 'long'). Default 'string'."""
        if name in self.values:
            return self.values.get(name, {}).get("type", "string")

    def _define_parameters(self):
        """Override in subclasses to register parameters via `add_parameter()`."""
        pass
