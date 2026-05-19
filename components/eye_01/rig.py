"""
EyeRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...builder import naming
from ...core import transform, control, matrix_constraint


class EyeRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)
        self.aim_transform = self.helpers["aim"]
        self.aim_master = self.data["parameters"].get("aim_master")
        self.eye_offset = None
        self.eye_ctrl = None
        self.aim_ctrl = None
        self.aim_offset = None

    def add_objects(self):
        self._add_group()
        self._update_rotation()
        self._create_joints()
        self._create_eye_ctrl()
        self._create_aim_ctrl()

    def add_operators(self):
        matrix_constraint.matrix_parent_constraint(self.eye_ctrl, self.jnts[0])

        # Aim constraint
        aim_vector = (1, 0, 0) if self.side == "right" else (-1, 0, 0)

        if self.side == "left":
            matrix_constraint.matrix_aim_constraint(
                driver=self.aim_ctrl,
                driven=self.eye_ctrl.getParent(),
                up_object=self.eye_offset,
                primary_axis=(-1, 0, 0),
            )
        else:
            matrix_constraint.matrix_aim_constraint(
                driver=self.aim_ctrl,
                driven=self.eye_ctrl.getParent(),
                up_object=self.eye_offset,
                primary_axis=(1, 0, 0),
            )

    def _update_rotation(self):
        positions = [
            om.MPoint(
                self.transforms[i][12], self.transforms[i][13], self.transforms[i][14]
            )
            for i in self.transforms
        ]
        aim_point = om.MPoint(
            self.aim_transform[12], self.aim_transform[13], self.aim_transform[14]
        )
        positions.append(aim_point)

        up_vector = om.MVector(0, 0, 1)
        if self.side == "right":
            mtxs = transform.chain_orient_from_positions(
                positions, up_vector, aim_axis="+x", up_axis="+y"
            )
        else:
            mtxs = transform.chain_orient_from_positions(
                positions, up_vector, aim_axis="-x", up_axis="-y"
            )
        keys = list(self.transforms.keys())
        for i, mtx in enumerate(mtxs):
            if i < 1:
                self.transforms[keys[i]] = list(mtx)

    def _create_aim_ctrl(self):
        aim_ctrl_name = self._get_name("aim", self.config.get("control"))
        aim_offset_name = self._get_name("aim", self.config.get("offset"))

        self.aim_offset, aim_ctrl = control.create_control(
            aim_ctrl_name,
            aim_offset_name,
            target_matrix=self.aim_transform,
            parent=self.ctrl_grp,
        )
        self.aim_ctrl = aim_ctrl

    def _create_eye_ctrl(self):
        ctrl_name = self._get_name("eye", self.config.get("control"))
        offset_name = self._get_name("eye", self.config.get("offset"))
        buffer_name = self._get_name("eye", self.config.get("buffer"))

        target_mtx = list(self.transforms.values())[0]
        self.eye_offset, self.eye_ctrl = control.create_control(
            ctrl_name,
            offset_name,
            buffer_name=buffer_name,
            target_matrix=target_mtx,
            parent=self.ctrl_grp,
        )

    def _get_follow_parent_groups(self):
        return [self.eye_offset]

    def connect(self):
        super().connect()
        if not self.aim_master:
            return
        eye_master = self.builder.find_relative(self.aim_master)
        if not eye_master:
            print(f"Cannot find aim master: {self.aim_master}")
            return
        pm.parent(self.aim_offset, eye_master)
        print(f"Connecting {self.name} aim to {self.aim_master} -> {eye_master}")
