"""
SpineRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...core import transform, matrix_constraint, control


class SpineRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)
        self.root_ctrl = None
        self.root_extra_ctrl = None

    def add_objects(self):
        self._add_group()
        self._update_rotation()
        self._create_joints()
        self._create_root_ctrl()
        self._create_fk_chain()
        self._create_fk_ctrl()

    def add_operators(self):
        for jnt, ctrl in zip(self.fk_jnts, self.fk_ctrls):
            matrix_constraint.matrix_parent_constraint(ctrl, jnt)

        for jnt, fk_jnt in zip(self.jnts, self.fk_jnts):
            matrix_constraint.matrix_parent_constraint(fk_jnt, jnt)

    def _update_rotation(self):
        positions = [
            om.MPoint(
                self.transforms[i][12], self.transforms[i][13], self.transforms[i][14]
            )
            for i in self.transforms
        ]
        up_vector = om.MVector(0, 0, 1)
        mtxs = transform.chain_orient_from_positions(
            positions, up_vector=up_vector, aim_axis="y", up_axis="z"
        )
        keys = list(self.transforms.keys())
        for i, mtx in enumerate(mtxs):
            self.transforms[keys[i]] = list(mtx)

    def _resolve_size(self):
        return round(self.segment_length("root", "chest") / 10, 3) * 1.5

    def _create_root_ctrl(self):
        root_name = self._get_name("Root", self.config.get("control"))
        root_offset_name = self._get_name("Root", self.config.get("group"))
        root_extra_name = self._get_name("RootExtra", self.config.get("control"))
        root_extra_offset_name = self._get_name("RootExtra", self.config.get("group"))

        mtx = self.transforms["root"]

        _, self.root_extra_ctrl = control.create_control(
            name=root_extra_name,
            offset_name=root_extra_offset_name,
            parent=self.ctrl_grp,
            target_matrix=mtx,
            shape="square",
            color_rgb=self._resolve_color(),
            size=self._resolve_size() * 3,
        )
        _, self.root_ctrl = control.create_control(
            name=root_name,
            offset_name=root_offset_name,
            parent=self.root_extra_ctrl,
            target_matrix=mtx,
            shape="square",
            color_rgb=self._resolve_color(),
            size=self._resolve_size() * 3 * 0.9,
        )

    def _create_fk_ctrl(self, skip_last=0):
        fk_ctrl_grp_name = self._get_name(self.name + "_FK", self.config.get("group"))
        self.fk_ctrl_grp = pm.group(n=fk_ctrl_grp_name, p=self.ctrl_grp, em=True)

        current_parent = self.root_ctrl
        items = list(self.transforms.items())

        if skip_last:
            items = items[:-skip_last]
        for guide, mtx in items:
            ctrl_name = self._get_name(guide + "_FK", self.config.get("control"))
            offset_name = self._get_name(guide + "_FK", self.config.get("offset"))
            _, ctrl = control.create_control(
                ctrl_name,
                offset_name,
                target_matrix=mtx,
                parent=current_parent,
                rotate_axis="y",
                rotate_angle=90,
                color_rgb=self._resolve_color(),
                size=self._resolve_size(),
            )
            current_parent = ctrl
            self.fk_ctrls.append(ctrl)
