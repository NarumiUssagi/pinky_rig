"""
ControlRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...core import control


class ControlRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)
        self.ctrl = None

    def add_objects(self):
        self._add_group()
        self._create_ctrl()

    def add_relations(self):
        self.relatives["root"] = self.ctrl

    def _get_follow_parent_groups(self):
        return [pm.listRelatives(self.ctrl, p=True)[0]]

    def _create_ctrl(self):
        ctrl_name = self._get_name("root", self.config.get("control"))
        offset_name = self._get_name("root", self.config.get("offset"))
        target_mtx = list(self.transforms.values())[0]
        _, self.ctrl = control.create_control(
            ctrl_name,
            offset_name,
            target_matrix=target_mtx,
            parent=self.ctrl_grp,
            shape="square",
            size=2,
            rotate_axis="x",
            rotate_angle=90,
        )
