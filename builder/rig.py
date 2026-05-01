"""
Rig Class
"""

import pymel.core as pm

from . import naming
from ..core import joint, control, transform


class Rig(object):
    def __init__(self, config=None, data=None, rig_builder=None):
        self.config = config or naming.load_naming_config_from_json()
        self.data = data
        self.builder = rig_builder

        params = data.get("parameters", {})
        self.name = params.get("name", None)
        self.side = params.get("side", "middle")
        self.index = params.get("index", 0)
        self.settings = params
        self.transforms = data.get("transforms", {})
        self.helpers = data.get("helpers", {})
        self.parent = data.get("parent")

        self.pref_axis = "+z"
        self.jnts = []
        self.fk_ctrls = []
        self.ik_ctrls = []
        self.ik_jnts = []
        self.fk_jnts = []
        self.ik_handle = None
        self.settings_ctrl = None
        self.ctrl_grp = None
        self.fk_ctrl_grp = None
        self.ik_ctrl_grp = None
        self.settings_ctrl_grp = None
        self.setup_grp = None

        self.relatives = {}
        self.control_relatives = {}

    def _get_name(self, description=None, extension=None):
        ext = extension or None
        raw_side = self.side
        side = self.config.get(raw_side, raw_side)
        values = {
            "name": self.name,
            "side": side,
            "index": self.index,
            "description": description,
            "extension": ext,
        }
        return naming.get_name(self.config, values)

    def add_objects(self):
        pass

    def add_attributes(self):
        pass

    def add_operators(self):
        pass

    def add_relations(self):
        for i, name in enumerate(self.transforms.keys()):
            self.relatives[name] = self.jnts[i]

    def _add_group(self):
        ctrl_grp_name = self._get_name(
            self.config.get("control"), self.config.get("group")
        )
        setup_grp_name = self._get_name(
            self.config.get("setup"), self.config.get("group")
        )

        self.ctrl_grp = pm.group(n=ctrl_grp_name, p=self.builder.root_ctrl, em=True)
        self.setup_grp = pm.group(n=setup_grp_name, p=self.builder.setup_grp, em=True)

    def _update_rotation(self):
        pass

    def _create_joints(self):
        names = [self._get_name(g, self.config.get("joint")) for g in self.transforms]
        self.jnts = joint.create_joint_chain(
            self.transforms, names=names, parent=self.builder.joint_grp
        )

    def _create_fk_chain(self):
        names = [
            self._get_name(g + "_FK", self.config.get("joint")) for g in self.transforms
        ]
        self.fk_jnts = joint.create_joint_chain(
            self.transforms, names=names, parent=self.ctrl_grp
        )
        for j in self.fk_jnts:
            j.v.set(0)

    def _create_ik_chain(self):
        names = [
            self._get_name(g + "_IK", self.config.get("joint")) for g in self.transforms
        ]
        self.ik_jnts = joint.create_joint_chain(
            self.transforms, names=names, parent=self.ctrl_grp
        )
        for j in self.ik_jnts:
            j.v.set(0)

    def _create_fk_ctrl(self):
        fk_ctrl_grp_name = self._get_name(self.name + "_FK", self.config.get("group"))
        self.fk_ctrl_grp = pm.group(n=fk_ctrl_grp_name, p=self.ctrl_grp, em=True)

        current_parent = self.fk_ctrl_grp
        for _, (guide, mtx) in enumerate(self.transforms.items()):
            ctrl_name = self._get_name(guide + "_FK", self.config.get("control"))
            offset_name = self._get_name(guide + "_FK", self.config.get("offset"))
            _, ctrl = control.create_control(
                ctrl_name, offset_name, target_matrix=mtx, parent=current_parent
            )
            current_parent = ctrl
            self.fk_ctrls.append(ctrl)

    def _create_ik_ctrl(self):
        ik_ctrl_grp_name = self._get_name(self.name + "_IK", self.config.get("group"))
        self.ik_ctrl_grp = pm.group(n=ik_ctrl_grp_name, p=self.ctrl_grp, em=True)

        ik_ctrl_name = self._get_name("IK", self.config.get("control"))
        pv_ctrl_name = self._get_name("PV", self.config.get("control"))
        ik_offset_name = self._get_name("IK", self.config.get("offset"))
        pv_offset_name = self._get_name("PV", self.config.get("offset"))

        positions = [pm.xform(j, ws=1, q=1, t=1) for j in self.ik_jnts]
        pv_pos = transform.find_pole_vector_position(
            positions, distance_multiplier=1.0, prefer_axis=self.pref_axis
        )

        _, ik_ctrl = control.create_control(
            ik_ctrl_name,
            ik_offset_name,
            target_matrix=list(self.transforms.values())[-1],
            parent=self.ik_ctrl_grp,
        )
        _, pv_ctrl = control.create_control(
            pv_ctrl_name,
            pv_offset_name,
            target_position=pv_pos,
            parent=self.ik_ctrl_grp,
        )
        self.ik_ctrls = [ik_ctrl, pv_ctrl]

    def _create_settings_ctrl(self):
        settings_ctrl_grp_name = self._get_name(
            self.name + "_settings", self.config.get("group")
        )
        self.settings_ctrl_grp = pm.group(
            n=settings_ctrl_grp_name, p=self.ctrl_grp, em=True
        )

        ctrl_name = self._get_name("settings", self.config.get("control"))
        offset_name = self._get_name("settings", self.config.get("offset"))
        _, self.settings_ctrl = control.create_control(
            ctrl_name,
            offset_name,
            target_matrix=list(self.transforms.values())[0],
            parent=self.settings_ctrl_grp,
        )

    def connect(self):
        if not self.parent:
            return
        if ":" not in self.parent:
            print(f"{self.name} has invalid parent format: {self.parent}")
            return

        target = self.builder.find_relative(self.parent)
        print(f"Connecting {self.name} to {self.parent} -> {target}")
        if not target:
            return

        self._default_parent_connection(target)

    def _default_parent_connection(self, target):
        if self.jnts:
            pm.parent(self.jnts[0], target)

        for grp in self._get_follow_parent_groups():
            if grp:
                pm.parentConstraint(target, grp, mo=True)
                pm.scaleConstraint(target, grp, mo=True)

        if self.ik_jnts:
            pm.parentConstraint(target, self.ik_jnts[0], mo=True)
            pm.scaleConstraint(target, self.ik_jnts[0], mo=True)

    def _get_follow_parent_groups(self):
        return [self.fk_ctrl_grp, self.settings_ctrl_grp]


class RigBuilder(object):
    def __init__(self, config=None, data=None, registry=None):
        self.config = config
        self.data = data
        self.name = data["parameters"].get("name", None)
        self.registry = registry if registry else None
        self.components = []

        self.root_group = None
        self.guide_grp = None
        self.control_grp = None
        self.joint_grp = None
        self.model_grp = None
        self.setup_grp = None

        self.root_ctrl = None

    def _add_group(self):
        root_grp_name = (
            f"{self.name}_{self.config.get('rig')}_{self.config.get('group')}"
        )
        guide_grp_name = f"{self.config.get('guide')}_{self.config.get('group')}"
        control_grp_name = f"{self.config.get('control')}_{self.config.get('group')}"
        joint_grp_name = f"{self.config.get('joint')}_{self.config.get('group')}"
        model_grp_name = f"{self.config.get('model')}_{self.config.get('group')}"
        setup_grp_name = f"{self.config.get('setup')}_{self.config.get('group')}"

        self.root_group = create_group(root_grp_name)
        self.guide_grp = create_group(guide_grp_name, self.root_group)
        self.control_grp = create_group(control_grp_name, self.root_group)
        self.joint_grp = create_group(joint_grp_name, self.root_group)
        self.model_grp = create_group(model_grp_name, self.root_group)
        self.setup_grp = create_group(setup_grp_name, self.root_group)

    def _init_components(self):
        for comp_data in self.data["components"]:
            guide_type = comp_data["type"]
            rig_class = self.registry.get(guide_type, None)
            if rig_class:
                instance = rig_class(
                    config=self.config, data=comp_data, rig_builder=self
                )
                self.components.append(instance)

    def build(self):
        self._add_group()
        self._create_root_ctrl()
        self._init_components()

        for component in self.components:
            component.add_objects()
        for component in self.components:
            component.add_attributes()
        for component in self.components:
            component.add_operators()
        for component in self.components:
            component.add_relations()
        for component in self.components:
            component.connect()

        self._finalize()

    def find_relative(self, ref_string):
        tokens = ref_string.split(":")
        if len(tokens) < 4:
            return None
        name = tokens[0]
        side = tokens[1]
        try:
            index = int(tokens[2])
        except ValueError:
            print(f"Invalid index in ref_string: {ref_string}")
            return None
        output = tokens[3]

        for component in self.components:
            if (
                component.name == name
                and component.side == side
                and component.index == index
            ):
                return component.relatives.get(output)
        return None

    def _finalize(self):
        if pm.objExists(self.name + "_guide_grp"):
            pm.parent(self.name + "_guide_grp", self.guide_grp)
            pm.setAttr(self.guide_grp + ".v", 0)

    def _create_root_ctrl(self):
        root_name = self._get_name("Global", self.config.get("control"))
        root_offset_name = self._get_name("Global", self.config.get("group"))
        self.root_ctrl = control.create_control(
            name=root_name, offset_name=root_offset_name, parent=self.control_grp
        )[1]

    def _get_name(self, name, description=None):
        values = {
            "name": name,
            "side": self.config.get("middle", "M"),
            "index": 0,
            "description": description,
        }
        return naming.get_name(self.config, values)


def create_group(name=None, parent=None):
    if not name:
        raise ValueError("create_group requires a name")
    if pm.objExists(name):
        return pm.PyNode(name)

    if parent:
        return pm.group(n=name, em=True, p=parent)
    else:
        return pm.group(n=name, w=True, em=True)
