"""
ArmRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...core import transform, control


class ArmRig(Rig):
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
        self._create_ik_chain()
        self._create_fk_ctrl()
        self._create_ik_ctrl()
        self._create_settings_ctrl()

    def add_operators(self):
        # FK constraints
        for fk_ctrl, fk_jnt in zip(self.fk_ctrls, self.fk_jnts):
            pm.parentConstraint(fk_ctrl, fk_jnt, mo=True)
            pm.scaleConstraint(fk_ctrl, fk_jnt, mo=True)

        # IK setup
        ik_ctrl = self.ik_ctrls[0]
        pv_ctrl = self.ik_ctrls[1]
        self.ik_handle, _ = pm.ikHandle(
            sj=self.ik_jnts[0], ee=self.ik_jnts[-1], n=self._get_name("IK", "ikHandle")
        )
        pm.poleVectorConstraint(pv_ctrl, self.ik_handle)
        pm.orientConstraint(ik_ctrl, self.ik_jnts[-1], mo=1)
        pm.pointConstraint(ik_ctrl, self.ik_handle, mo=1)
        self.ik_handle.v.set(0)
        pm.parent(self.ik_handle, ik_ctrl)

        rev = pm.createNode("reverse", n=self._get_name("ikfk_blend", "reverse"))
        pm.connectAttr(self.settings_ctrl.ikfk_blend, rev.inputX, f=1)

        # Create constrain
        for i in range(3):
            par_con = pm.parentConstraint(
                self.fk_jnts[i], self.ik_jnts[i], self.jnts[i], mo=1
            )
            par_con.interpType.set(2)
            scale_con = pm.scaleConstraint(
                self.fk_jnts[i], self.ik_jnts[i], self.jnts[i], mo=1
            )
            par_tgts = pm.parentConstraint(par_con, q=1, wal=1)
            scale_tgt = pm.scaleConstraint(scale_con, q=1, wal=1)

            pm.connectAttr(self.settings_ctrl.ikfk_blend, par_tgts[1], f=1)
            pm.connectAttr(rev.outputX, par_tgts[0], f=1)
            pm.connectAttr(self.settings_ctrl.ikfk_blend, scale_tgt[1], f=1)
            pm.connectAttr(rev.outputX, scale_tgt[0], f=1)
            pm.connectAttr(rev.outputX, self.fk_ctrls[i].getParent().v, f=1)

        pm.connectAttr(
            self.settings_ctrl.ikfk_blend, self.ik_ctrls[0].getParent().v, f=1
        )
        pm.connectAttr(
            self.settings_ctrl.ikfk_blend, self.ik_ctrls[1].getParent().v, f=1
        )

    def add_attributes(self):
        default_blend = self.data["parameters"].get("ifk_blend", 0)
        pm.addAttr(
            self.settings_ctrl,
            ln="ikfk_blend",
            at="float",
            min=0,
            max=1,
            dv=default_blend,
            k=True,
        )

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
            if i < 3:
                self.transforms[keys[i]] = list(mtx)

    def _create_settings_ctrl(self):
        settings_ctrl_grp_name = self._get_name(
            self.name + "_settings", self.config.get("group")
        )
        self.settings_ctrl_grp = pm.group(
            n=settings_ctrl_grp_name, p=self.ctrl_grp, em=True
        )
        if self.side == "right":
            mtx = transform.get_offset_matrix(self.jnts[0], (0, 0, -2))
        elif self.side == "left":
            mtx = transform.get_offset_matrix(self.jnts[0], (0, 0, 2))
        else:
            mtx = transform.get_offset_matrix(self.jnts[0], (0, 2, 0))

        ctrl_name = self._get_name("settings", self.config.get("control"))
        offset_name = self._get_name("settings", self.config.get("offset"))
        _, self.settings_ctrl = control.create_control(
            ctrl_name,
            offset_name,
            target_matrix=mtx,
            parent=self.settings_ctrl_grp,
        )
