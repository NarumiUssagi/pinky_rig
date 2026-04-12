"""
SpineRig Class
"""

import pymel.core as pm

from ...builder.rig import Rig


class SpineRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)

    def add_objects(self):
        self._add_group()
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

    def add_relations(self):
        self.relatives["root"] = self.jnts[0]
        self.relatives["spine"] = self.jnts[1]
        self.relatives["chest"] = self.jnts[2]
