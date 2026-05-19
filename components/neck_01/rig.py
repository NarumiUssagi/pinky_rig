"""
NeckRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...core import transform, matrix_constraint


class NeckRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)

    def add_objects(self):
        self._add_group()
        self._update_rotation()
        self._create_joints()
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
        mtxs = transform.chain_orient_from_positions(positions, up_vector)
        keys = list(self.transforms.keys())
        for i, mtx in enumerate(mtxs):
            self.transforms[keys[i]] = list(mtx)
