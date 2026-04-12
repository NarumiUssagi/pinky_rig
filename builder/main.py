"""
Main Class
"""


class Main(object):
    def __init__(self):
        self.values = {}
        self._define_parameters()

    def add_parameter(self, name, value=None, at_type="string"):
        if name in self.values:
            print(f"{name} is already in parameters.")
            return
        self.values[name] = {"value": value, "type": at_type}

    def remove_parameter(self, name):
        if name in self.values:
            self.values.pop(name, None)
        else:
            print(f"{name} is not in parameters.")

    def get_parameter_value(self, name):
        try:
            return self.values[name]["value"]
        except KeyError:
            print(f"{name} is not in parameters.")

    def set_parameter_value(self, name, value):
        if name in self.values:
            self.values[name]["value"] = value
        else:
            print(f"{name} is not in parameters.")

    def get_parameter_type(self, name):
        if name in self.values:
            return self.values.get(name, {}).get("type", "string")

    def _define_parameters(self):
        pass
