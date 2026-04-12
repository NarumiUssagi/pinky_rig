"""
ArmRig Class
"""

import pymel.core as pm

from ...builder.rig import Rig


class ArmRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)

    def add_objects(self):
        self._add_group()
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
        # pylint: disable-next=assignment-from-no-return
        self.ik_handle, _ = pm.ikHandle(
            sj=self.ik_jnts[0], ee=self.ik_jnts[-1], n=self._get_name("IK", "ikHandle")
        )
        pm.poleVectorConstraint(pv_ctrl, self.ik_handle)
        pm.orientConstraint(ik_ctrl, self.ik_jnts[-1], mo=1)
        pm.pointConstraint(ik_ctrl, self.ik_handle, mo=1)
        self.ik_handle.v.set(0)
        pm.parent(self.ik_handle, ik_ctrl)

        # pylint: disable-next=assignment-from-no-return
        rev = pm.createNode("reverse", n=self._get_name("ikfk_blend", "reverse"))
        pm.connectAttr(self.settings_ctrl.ikfk_blend, rev.inputX, f=1)

        # Create constrain
        for i in range(3):
            # pylint: disable-next=assignment-from-no-return
            par_con = pm.parentConstraint(
                self.fk_jnts[i], self.ik_jnts[i], self.jnts[i], mo=1
            )
            par_con.interpType.set(2)
            # pylint: disable-next=assignment-from-no-return
            scale_con = pm.scaleConstraint(
                self.fk_jnts[i], self.ik_jnts[i], self.jnts[i], mo=1
            )
            # pylint: disable-next=assignment-from-no-return
            par_tgts = pm.parentConstraint(par_con, q=1, wal=1)
            # pylint: disable-next=assignment-from-no-return
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

    def add_relations(self):
        self.relatives["root"] = self.jnts[0]
        self.relatives["elbow"] = self.jnts[1]
        self.relatives["wrist"] = self.jnts[2]
