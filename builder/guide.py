"""
Guide Class
"""

import pymel.core as pm

from .main import Main
from . import naming
from ..core import transform


class Guide(Main):
    def __init__(self, name=None, side="middle", index=0, config=None):
        super().__init__()
        self.config = config or naming.load_naming_config_from_json()

        self.parent = None
        self.save_transform = []
        self.save_helpers = []

        if name:
            self.set_parameter_value("name", name)
        self.set_parameter_value("side", side)
        self.set_parameter_value("index", index)

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("type", self.__class__.__name__, at_type="string")
        self.add_parameter("name", "guide", at_type="string")
        self.add_parameter("side", "M", at_type="string")
        self.add_parameter("index", 0, at_type="long")

    def add_root(self, name="root", parent=None, position=None):
        root = self.add_loc(name, parent, position)
        if not root:
            return
        # Add parameter to attributes
        for parameter in self.values:
            if root.hasAttr(parameter):
                continue
            val = self.get_parameter_value(parameter)
            typ = self.get_parameter_type(parameter)
            if typ == "string":
                pm.addAttr(root, ln=parameter, dt="string")
                if val:
                    root.attr(parameter).set(str(val))
            else:
                try:
                    pm.addAttr(root, ln=parameter, at=typ, k=True)
                    if val is not None:
                        root.attr(parameter).set(val)
                except RuntimeError:
                    pm.warning(f"Please check the type of parameter {name}.{typ}")

        return root

    def add_loc(self, name, parent=None, position=None):
        loc = pm.spaceLocator(name=name)  # pylint: disable=assignment-from-no-return
        if parent:
            if not pm.objExists(parent):
                print(f"Parent {parent} doesn't exist")
                return
            loc.setParent(parent)
        mtx = position if position else pm.datatypes.Matrix()
        pm.xform(loc, a=1, ws=1, m=mtx)
        return loc

    def _get_name(self, description=None):
        extension = self.config.get("guide", "guide")
        raw_side = self.get_parameter_value("side")
        side = self.config.get(raw_side, raw_side)
        values = {
            "name": self.get_parameter_value("name"),
            "side": side,
            "index": self.get_parameter_value("index"),
            "description": description,
            "extension": extension,
        }
        return naming.get_name(self.config, values)

    def set_index(self):
        while True:
            name = self._get_name("root")
            if pm.objExists(name):
                current_index = self.get_parameter_value("index")
                self.set_parameter_value("index", current_index + 1)
            else:
                break

    def add_objects(self):
        raise NotImplementedError

    def post_draw(self):
        pass

    def draw(self, parent=None, use_existing_index=False):
        if isinstance(parent, (list, tuple)):
            parent = parent[0] if parent else None
        self.parent = parent
        if not use_existing_index:
            self.set_index()
        self.add_objects()
        self.post_draw()

    def read_from_scene(self):
        root_name = self._get_name("root")
        if not pm.objExists(root_name):
            pm.warning(f"Component root {root_name} doesn't exist,please build first")
            return ([], [])
        root = pm.PyNode(root_name)
        for name in self.values:
            # pylint: disable=no-member
            if root.hasAttr(name):
                val = root.attr(name).get()
                self.set_parameter_value(name, val)

        transforms = {}
        for t in self.save_transform:
            full_name = self._get_name(description=t)
            if pm.objExists(full_name):
                # pylint: disable-too-many-function-args
                transforms[t] = pm.xform(full_name, q=True, ws=True, m=True)

        helpers = {}
        for h in self.save_helpers:
            full_name = self._get_name(description=h)
            if pm.objExists(full_name):
                # pylint: disable-too-many-function-args
                helpers[h] = pm.xform(full_name, q=True, ws=True, m=True)

        return transforms, helpers

    def update(self, transforms=None, helpers=None):
        if transforms:
            for t in self.save_transform:
                full_name = self._get_name(description=t)
                if t not in transforms:
                    print(f"'{t}' not found in transforms data")
                    continue
                if not pm.objExists(full_name):
                    pm.warning(f"'{full_name}' not found in scene")
                    continue
                pm.xform(full_name, a=True, ws=True, m=transforms[t])
        if helpers:
            for h in self.save_helpers:
                full_name = self._get_name(description=h)
                if h not in helpers:
                    print(f"'{h}' not found in helpers data")
                    continue
                if not pm.objExists(full_name):
                    pm.warning(f"'{full_name}' not found in scene, creating new one")
                pm.xform(full_name, a=True, ws=True, m=helpers[h])

    def serialize(self):
        transforms, helpers = self.read_from_scene()
        if not transforms:
            return
        data = {
            "type": self.__class__.__name__,
            "parameters": {
                name: self.get_parameter_value(name) for name in self.values
            },
            "transforms": transforms,
            "helpers": helpers,
            "parent": str(self.parent) if self.parent else None,
        }
        return data

    def deserialize(self, data=None):
        if not isinstance(data, dict):
            return
        for name, value in data["parameters"].items():
            self.set_parameter_value(name, value)
        self.parent = data.get("parent")

    @property
    def root_name(self):
        return self._get_name("root")


class RigGuide(Main):
    def __init__(self, name="rig"):
        self.name = name
        self.default_config = naming.load_naming_config_from_json()
        super().__init__()
        self.components = []
        self.root_group = None

    def _define_parameters(self):
        self.add_parameter("name", self.name, "string")
        self.add_parameter(
            "naming_rule",
            self.default_config.get(
                "naming_rule", "{name}_{side}{index}_{description}_{extension}"
            ),
            "string",
        )
        self.add_parameter("left", self.default_config.get("left", "L"), "string")
        self.add_parameter("right", self.default_config.get("right", "R"), "string")
        self.add_parameter("middle", self.default_config.get("middle", "M"), "string")
        self.add_parameter(
            "control", self.default_config.get("control", "ctrl"), "string"
        )
        self.add_parameter("guide", self.default_config.get("guide", "guide"), "string")
        self.add_parameter("rig", self.default_config.get("rig", "rig"), "string")
        self.add_parameter("joint", self.default_config.get("joint", "jnt"), "string")
        self.add_parameter("group", self.default_config.get("group", "grp"), "string")
        self.add_parameter("model", self.default_config.get("model", "model"), "string")
        self.add_parameter(
            "offset", self.default_config.get("offset", "offset"), "string"
        )
        self.add_parameter("setup", self.default_config.get("setup", "setup"), "string")
        self.add_parameter(
            "buffer", self.default_config.get("buffer", "buffer"), "string"
        )

    def add_component(self, component=None, parent=None):
        if isinstance(component, Guide):
            self.components.append(component)
            if not parent:
                component.parent = self.grp_name
            else:
                component.parent = parent
        else:
            print(f"Invalid component: {component}. It should be an instance of Guide.")

    def remove_component(self, component=None):
        if component in self.components:
            self.components.remove(component)

    def _add_group(self):
        if pm.objExists(self.grp_name):
            group = pm.PyNode(self.grp_name)
        else:
            group = pm.group(n=self.grp_name, w=True, em=True)
        self.root_group = group

        # Add attributes
        for parameter in self.values:
            if group.hasAttr(parameter):
                continue
            val = self.get_parameter_value(parameter)
            typ = self.get_parameter_type(parameter)
            if typ == "string":
                pm.addAttr(group, ln=parameter, dt="string")
                if val:
                    group.attr(parameter).set(str(val))
            else:
                pm.addAttr(group, ln=parameter, at=typ, k=True)
                if val is not None:
                    group.attr(parameter).set(val)

        return group

    def _add_objects(self):
        missing = []

        for component in self.components:
            original_parent = component.parent
            scene_parent = original_parent
            if original_parent and ":" in original_parent:
                scene_parent = self._resolve_parent(original_parent)
                if not pm.objExists(scene_parent):
                    missing.append((component.root_name, original_parent, scene_parent))

            elif not original_parent:
                scene_parent = self.grp_name
            component.draw(scene_parent)
            component.parent = original_parent

        if missing:
            msg = "Failed to resolve parents for components:\n" + "\n".join(
                f"  {root} -> '{decl}' (resolved: '{tgt}')"
                for root, decl, tgt in missing
            )
            raise RuntimeError(msg)

    def draw(self):
        self._add_group()
        self._add_objects()

    def read_from_scene(self):
        if not pm.objExists(self.grp_name):
            return
        group = pm.PyNode(self.grp_name)
        for name in self.values:
            # pylint: disable=no-member
            if group.hasAttr(name):
                val = group.attr(name).get()
                self.set_parameter_value(name, val)

    def serialize(self):
        sub_datas = []
        for component in self.components:
            sub_datas.append(component.serialize())
        self.read_from_scene()
        data = {
            "type": self.__class__.__name__,
            "parameters": {
                name: self.get_parameter_value(name) for name in self.values
            },
            "components": sub_datas,
        }
        return data

    def deserialize(self, data=None, registry=None):
        if not isinstance(data, dict):
            return
        for name, value in data["parameters"].items():
            self.set_parameter_value(name, value)
        self.name = self.get_parameter_value("name")
        self._add_group()

        for comp_data in data["components"]:
            guide_type = comp_data["type"]
            guide_class = registry.get(guide_type)
            if guide_class:
                instance = guide_class(config=self.naming_config)
                self.add_component(instance, parent=comp_data.get("parent"))
                instance.deserialize(comp_data)

        self._add_objects()

        for comp_data, component in zip(data["components"], self.components):
            component.update(
                transforms=comp_data.get("transforms"),
                helpers=comp_data.get("helpers"),
            )

    def _resolve_parent(self, parent):
        # parent_sample : "Spine:middle:0:chest"
        tokens = parent.split(":")
        if len(tokens) < 4:
            print(f"Invalid parent reference: {parent}")
            return self.grp_name
        name_token = tokens[0]
        side_token = self.naming_config.get(tokens[1], tokens[1])
        try:
            index_token = int(tokens[2])
        except ValueError:
            print(f"Invalid index in parent reference: {parent}")
            return self.grp_name
        description_token = tokens[3]
        extension_token = self.naming_config.get("guide", "guide")
        values = {
            "name": name_token,
            "side": side_token,
            "index": index_token,
            "description": description_token,
            "extension": extension_token,
        }
        return naming.get_name(self.naming_config, values)

    def mirror_components(self, component=None, registry=None):
        if not component:
            return
        comp_data = component.serialize()
        if not comp_data:
            return
        guide_type = comp_data["type"]
        guide_class = registry.get(guide_type)
        parent = comp_data.get("parent")

        # Mirror side in parent reference
        if "right" in parent:
            parent = parent.replace("right", "left")
        elif "left" in parent:
            parent = parent.replace("left", "right")

        instance = guide_class(config=self.naming_config)
        self.add_component(instance, parent)
        if pm.objExists(self.grp_name):
            comp_data["parameters"]["side"] = (
                "left" if comp_data["parameters"]["side"] == "right" else "right"
            )
            for key in comp_data["transforms"]:
                comp_data["transforms"][key] = transform.mirror_matrix_yz(
                    comp_data["transforms"][key]
                )
            for key in comp_data["helpers"]:
                comp_data["helpers"][key] = transform.mirror_matrix_yz_translation_only(
                    comp_data["helpers"][key]
                )
            instance.deserialize(comp_data)
            instance.draw(parent=self._resolve_parent(parent))
            instance.update(
                transforms=comp_data["transforms"], helpers=comp_data.get("helpers")
            )
            instance.parent = parent

    def mirror_all(self, registry=None):
        for component in list(self.components):
            side = component.get_parameter_value("side")
            if side in ("left", "right"):
                self.mirror_components(component, registry=registry)

    @property
    def grp_name(self):
        grp_name = f"{self.get_parameter_value('name')}_{self.naming_config.get('guide','guide')}_{self.naming_config.get('group','grp')}"
        return grp_name

    @property
    def naming_config(self):
        config = {
            "naming_rule": self.get_parameter_value("naming_rule"),
            "naming_tokens": [
                "name",
                "side",
                "index",
                "description",
                "extension",
            ],
            "left": self.get_parameter_value("left"),
            "right": self.get_parameter_value("right"),
            "middle": self.get_parameter_value("middle"),
            "control": self.get_parameter_value("control"),
            "guide": self.get_parameter_value("guide"),
            "rig": self.get_parameter_value("rig"),
            "joint": self.get_parameter_value("joint"),
            "group": self.get_parameter_value("group"),
            "model": self.get_parameter_value("model"),
            "offset": self.get_parameter_value("offset"),
            "setup": self.get_parameter_value("setup"),
            "buffer": self.get_parameter_value("buffer"),
        }
        return config
