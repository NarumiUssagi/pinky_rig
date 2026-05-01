"""
LegRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...core import transform, control


class LegRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)
        self.up_transform = self.helpers["upv"]
        self.eff_transform = self.helpers["eff"]
        self.reverse_foot_locs = []
        self.toe_tip_ctrl = None
        self.roll_ctrl = None
        self.heel_ctrl = None
        self.eff_ctrl = None

    def add_objects(self):
        self._add_group()
        self._update_rotation()
        self._create_joints()
        self._create_fk_chain()
        self._create_ik_chain()
        self._create_fk_ctrl()
        self._create_ik_ctrl()
        self._create_settings_ctrl()
        self._create_reverse_foot_ctrl()

    def add_operators(self):
        # FK constraints
        for fk_ctrl, fk_jnt in zip(self.fk_ctrls, self.fk_jnts):
            pm.parentConstraint(fk_ctrl, fk_jnt, mo=True)
            pm.scaleConstraint(fk_ctrl, fk_jnt, mo=True)

        # IK setup
        ik_ctrl = self.ik_ctrls[0]
        pv_ctrl = self.ik_ctrls[1]
        self.ik_handle, _ = pm.ikHandle(
            sj=self.ik_jnts[0], ee=self.ik_jnts[-3], n=self._get_name("IK", "ikHandle")
        )

        # Reverse foot ik handle
        toe_ik_handle, _ = pm.ikHandle(
            sj=self.ik_jnts[-3],
            ee=self.ik_jnts[-2],
            n=self._get_name("IK_toe", "ikHandle"),
        )
        toe_end_ik_handle, _ = pm.ikHandle(
            sj=self.ik_jnts[-2],
            ee=self.ik_jnts[-1],
            n=self._get_name("IK_toeEnd", "ikHandle"),
        )

        pm.poleVectorConstraint(pv_ctrl, self.ik_handle)
        pm.scaleConstraint(ik_ctrl, self.ik_jnts[-3], mo=1)
        self.ik_handle.v.set(0)
        toe_ik_handle.v.set(0)
        toe_end_ik_handle.v.set(0)
        pm.parent(self.ik_handle, self.reverse_foot_locs[-1])
        pm.parent(toe_ik_handle, self.reverse_foot_locs[-1])
        pm.parent(toe_end_ik_handle, self.toe_tip_ctrl)

        rev = pm.createNode("reverse", n=self._get_name("ikfk_blend", "reverse"))
        pm.connectAttr(self.settings_ctrl.ikfk_blend, rev.inputX, f=1)

        # Create constrain
        for i in range(4):
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

        # Connect reverse foot

        # Bank
        bank_cod = pm.createNode("condition", n=self._get_name("bank", "cod"))
        pm.connectAttr(ik_ctrl.foot_bank, bank_cod.firstTerm)
        bank_cod.operation.set(2)
        pm.connectAttr(ik_ctrl.foot_bank, bank_cod.colorIfFalseR)
        pm.connectAttr(ik_ctrl.foot_bank, bank_cod.colorIfTrueG)
        bank_cod.colorIfFalseG.set(0)
        pm.connectAttr(bank_cod.outColorR, self.reverse_foot_locs[0].rz)
        pm.connectAttr(bank_cod.outColorG, self.reverse_foot_locs[1].rz)

        # Toe Tap
        pm.connectAttr(ik_ctrl.toe_tap, self.toe_tip_ctrl.getParent().rz)

        # Roll
        roll_cod = pm.createNode("condition", n=self._get_name("rollSplit", "cod"))
        roll_diff = pm.createNode(
            "plusMinusAverage", n=self._get_name("rollDiff", "pma")
        )
        roll_mirror = pm.createNode(
            "plusMinusAverage", n=self._get_name("rollMirror", "pma")
        )
        roll_eff_pos = pm.createNode(
            "multiplyDivide", n=self._get_name("rollEffPos", "md")
        )
        roll_toe_neg = pm.createNode(
            "multiplyDivide", n=self._get_name("rollToeNeg", "md")
        )
        roll_clamp = pm.createNode("clamp", n=self._get_name("rollToeClamp", "clamp"))

        pm.connectAttr(ik_ctrl.foot_roll, roll_cod.firstTerm)
        roll_cod.operation.set(2)
        pm.connectAttr(ik_ctrl.foot_roll_start, roll_cod.secondTerm)

        roll_diff.operation.set(2)
        pm.connectAttr(ik_ctrl.foot_roll_start, roll_diff.input1D[0])
        pm.connectAttr(ik_ctrl.foot_roll, roll_diff.input1D[1])

        roll_mirror.operation.set(1)
        pm.connectAttr(roll_diff.output1D, roll_mirror.input1D[0])
        pm.connectAttr(ik_ctrl.foot_roll_start, roll_mirror.input1D[1])

        pm.connectAttr(ik_ctrl.foot_roll, roll_cod.colorIfFalseR)
        pm.connectAttr(roll_mirror.output1D, roll_cod.colorIfTrueR)

        roll_eff_pos.input1X.set(-1)
        pm.connectAttr(roll_diff.output1D, roll_eff_pos.input2X)
        pm.connectAttr(roll_eff_pos.outputX, roll_cod.colorIfTrueG)
        roll_cod.colorIfFalseG.set(0)

        roll_toe_neg.input1X.set(-1)
        pm.connectAttr(roll_cod.outColorR, roll_toe_neg.input2X)
        pm.connectAttr(roll_cod.outColorG, self.eff_ctrl.getParent().rx)

        pm.connectAttr(roll_toe_neg.outputX, roll_clamp.inputR)
        roll_clamp.minR.set(-9999)
        roll_clamp.maxR.set(0)
        pm.connectAttr(roll_clamp.outputR, self.roll_ctrl.getParent().rz)

        # Heel
        heel_cod = pm.createNode("condition", n=self._get_name("heel", "cod"))
        pm.connectAttr(ik_ctrl.foot_roll, heel_cod.firstTerm)
        pm.connectAttr(ik_ctrl.foot_roll, heel_cod.colorIfTrueR)
        heel_cod.operation.set(4)
        heel_cod.colorIfFalseR.set(0)
        pm.connectAttr(heel_cod.outColorR, self.heel_ctrl.getParent().rx)

    def add_attributes(self):
        default_blend = self.data["parameters"].get("ifk_blend", 0.0)
        pm.addAttr(
            self.settings_ctrl,
            ln="ikfk_blend",
            at="double",
            min=0,
            max=1,
            dv=default_blend,
            k=True,
        )
        defult_foot_roll_value = self.data["parameters"].get("foot_roll", 0.0)
        pm.addAttr(
            self.ik_ctrls[0],
            ln="foot_roll",
            at="double",
            dv=defult_foot_roll_value,
            k=True,
        )
        defult_foot_roll_start_value = self.data["parameters"].get(
            "foot_roll_start", 0.0
        )
        pm.addAttr(
            self.ik_ctrls[0],
            ln="foot_roll_start",
            at="double",
            dv=defult_foot_roll_start_value,
            k=True,
        )
        defult_foot_bank_value = self.data["parameters"].get("bank", 0.0)
        pm.addAttr(
            self.ik_ctrls[0],
            ln="foot_bank",
            at="double",
            dv=defult_foot_bank_value,
            k=True,
        )
        defult_toe_tap_value = self.data["parameters"].get("toe_tap", 0.0)
        pm.addAttr(
            self.ik_ctrls[0],
            ln="toe_tap",
            at="double",
            dv=defult_toe_tap_value,
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
            if i < 5:
                self.transforms[keys[i]] = list(mtx)

    def _create_ik_ctrl(self):
        ik_ctrl_grp_name = self._get_name(self.name + "_IK", self.config.get("group"))
        self.ik_ctrl_grp = pm.group(n=ik_ctrl_grp_name, p=self.ctrl_grp, em=True)

        ik_ctrl_name = self._get_name("IK", self.config.get("control"))
        pv_ctrl_name = self._get_name("PV", self.config.get("control"))
        ik_offset_name = self._get_name("IK", self.config.get("offset"))
        pv_offset_name = self._get_name("PV", self.config.get("offset"))

        positions = [pm.xform(j, ws=1, q=1, t=1) for j in self.ik_jnts][:-2]
        pv_pos = transform.find_pole_vector_position(
            positions, distance_multiplier=1.0, prefer_axis=self.pref_axis
        )

        _, ik_ctrl = control.create_control(
            ik_ctrl_name,
            ik_offset_name,
            target_matrix=list(self.transforms.values())[-3],
            parent=self.ik_ctrl_grp,
        )
        _, pv_ctrl = control.create_control(
            pv_ctrl_name,
            pv_offset_name,
            target_position=pv_pos,
            parent=self.ik_ctrl_grp,
        )
        self.ik_ctrls = [ik_ctrl, pv_ctrl]

    def _create_fk_ctrl(self):
        fk_ctrl_grp_name = self._get_name(self.name + "_FK", self.config.get("group"))
        self.fk_ctrl_grp = pm.group(n=fk_ctrl_grp_name, p=self.ctrl_grp, em=True)

        current_parent = self.fk_ctrl_grp
        for i, (guide, mtx) in enumerate(self.transforms.items()):
            if i < len(self.transforms.items()) - 1:
                ctrl_name = self._get_name(guide + "_FK", self.config.get("control"))
                offset_name = self._get_name(guide + "_FK", self.config.get("offset"))
                _, ctrl = control.create_control(
                    ctrl_name, offset_name, target_matrix=mtx, parent=current_parent
                )
                current_parent = ctrl
                self.fk_ctrls.append(ctrl)

    def _create_settings_ctrl(self):
        settings_ctrl_grp_name = self._get_name(
            self.name + "_settings", self.config.get("group")
        )
        self.settings_ctrl_grp = pm.group(
            n=settings_ctrl_grp_name, p=self.ctrl_grp, em=True
        )
        if self.side == "right":
            mtx = transform.get_offset_matrix(self.jnts[0], (0, 0, 2))
        elif self.side == "left":
            mtx = transform.get_offset_matrix(self.jnts[0], (0, 0, -2))
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

    def _create_reverse_foot_ctrl(self):
        loc_transform = [
            self.helpers["sideInner"],
            self.helpers["sideOuter"],
            self.helpers["heel"],
            self.helpers["eff"],
            self.transforms["toe"],
        ]

        # Create side groups
        grp_names = ["sideInner", "sideOuter"]
        for i, t in enumerate(loc_transform[:2]):
            # Create offset group
            offset_grp = pm.group(
                em=True,
                n=self._get_name(grp_names[i], self.config.get("offset")),
            )
            pm.xform(offset_grp, ws=True, m=t)

            # Parent offset group
            if i > 0:
                pm.parent(offset_grp, self.reverse_foot_locs[-1])
            else:
                pm.parent(offset_grp, self.ik_ctrls[0])

            # Create buffer group
            buffer_grp = pm.group(
                em=True,
                n=self._get_name(grp_names[i], self.config.get("buffer")),
                p=offset_grp,
            )
            self.reverse_foot_locs.append(buffer_grp)

        # Create reverse foot ctrl
        loc_names = ["heel", "eff", "toe"]
        for i, t in enumerate(loc_transform[2:]):
            reveser_foot_ctrl_name = self._get_name(
                loc_names[i], self.config.get("control")
            )
            reveser_foot_offset_name = self._get_name(
                loc_names[i], self.config.get("offset")
            )
            reveser_foot_buffer_name = self._get_name(
                loc_names[i], self.config.get("buffer")
            )

            _, current_ctrl = control.create_control(
                reveser_foot_ctrl_name,
                reveser_foot_offset_name,
                buffer_name=reveser_foot_buffer_name,
                target_matrix=t,
                parent=self.reverse_foot_locs[-1],
            )
            self.reverse_foot_locs.append(current_ctrl)

        toe_tip_ctrl_name = self._get_name("toeTip", self.config.get("control"))
        toe_tip_offset_name = self._get_name("toeTip", self.config.get("offset"))
        toe_tip_buffer_name = self._get_name("toeTip", self.config.get("buffer"))

        _, toe_tip_ctrl = control.create_control(
            toe_tip_ctrl_name,
            toe_tip_offset_name,
            buffer_name=toe_tip_buffer_name,
            target_matrix=self.transforms["toe"],
            parent=self.reverse_foot_locs[-2],
        )

        self.toe_tip_ctrl = toe_tip_ctrl
        self.roll_ctrl = self.reverse_foot_locs[-1]
        self.eff_ctrl = self.reverse_foot_locs[-2]
        self.heel_ctrl = self.reverse_foot_locs[-3]
