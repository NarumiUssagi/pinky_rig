"""
ShoulderRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...core import transform


class ShoulderRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)
        self.up_transform = self.helpers["upv"]
        self.eff_transform = self.helpers["eff"]
        self.pref_axis = "-z"

    def add_objects(self):
        self._add_group()
        self._update_rotation()
        self._create_joints()
        self._create_fk_chain()
        self._create_fk_ctrl()

    def add_operators(self):
        for jnt, ctrl in zip(self.fk_jnts, self.fk_ctrls):
            pm.parentConstraint(ctrl, jnt, mo=True)
            pm.scaleConstraint(ctrl, jnt, mo=True)

        for jnt, fk_jnt in zip(self.jnts, self.fk_jnts):
            pm.parentConstraint(fk_jnt, jnt, mo=True)
            pm.scaleConstraint(fk_jnt, jnt, mo=True)

    def _update_rotation(self):
        positions = [
            om.MPoint(
                self.transforms[i][12], self.transforms[i][13], self.transforms[i][14]
            )
            for i in self.transforms
        ]
        root_point = positions[0]
        upv_point = om.MPoint(
            self.up_transform[12], self.up_transform[13], self.up_transform[14]
        )
        eff_point = om.MPoint(
            self.eff_transform[12], self.eff_transform[13], self.eff_transform[14]
        )
        positions.append(eff_point)

        up_vector = upv_point - root_point
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
