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
        self.toe_transform = self.transforms["toe"]
        self.up_transform = self.helpers["upv"]
        self.eff_transform = self.helpers["eff"]
        self.side_inner_transform = self.helpers["sideInner"]
        self.side_outer_transform = self.helpers["sideOuter"]
        self.heel_transform = self.helpers["heel"]
        self.reverse_foot_locs = []

    def add_objects(self):
        self._add_group()
        self._update_rotation()
        self._create_joints()
        self._create_fk_chain()
        self._create_ik_chain()
        self._create_fk_ctrl()
        self._create_ik_ctrl()
        self._create_settings_ctrl()
        self._create_reverse_foot_loc()

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
            sj=self.ik_jnts[0], ee=self.ik_jnts[-3], n=self._get_name("IK", "ikHandle")
        )

        # Reverse foot ik handle
        # pylint: disable-next=assignment-from-no-return
        toe_ik_handle, _ = pm.ikHandle(
            sj=self.ik_jnts[-3],
            ee=self.ik_jnts[-2],
            n=self._get_name("IK_toe", "ikHandle"),
        )
        # pylint: disable-next=assignment-from-no-return
        toe_end_ik_handle, _ = pm.ikHandle(
            sj=self.ik_jnts[-2],
            ee=self.ik_jnts[-1],
            n=self._get_name("IK_toeEnd", "ikHandle"),
        )

        pm.poleVectorConstraint(pv_ctrl, self.ik_handle)
        # pm.orientConstraint(ik_ctrl, self.ik_jnts[-3], mo=1)
        pm.scaleConstraint(ik_ctrl, self.ik_jnts[-3], mo=1)
        self.ik_handle.v.set(0)
        toe_ik_handle.v.set(0)
        toe_end_ik_handle.v.set(0)
        pm.parent(self.ik_handle, self.reverse_foot_locs[-2])
        pm.parent(toe_ik_handle, self.reverse_foot_locs[-2])
        pm.parent(toe_end_ik_handle, self.reverse_foot_locs[-1])

        # pylint: disable-next=assignment-from-no-return
        rev = pm.createNode("reverse", n=self._get_name("ikfk_blend", "reverse"))
        pm.connectAttr(self.settings_ctrl.ikfk_blend, rev.inputX, f=1)

        # Create constrain
        for i in range(4):
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
        default_blend = self.data["parameters"].get("ifk_blend", 0.0)
        pm.addAttr(
            self.settings_ctrl,
            ln="ikfk_blend",
            at="float",
            min=0,
            max=1,
            dv=default_blend,
            k=True,
        )
        defult_foot_roll_value = self.data["parameters"].get("foot_roll", 0.0)
        pm.addAttr(
            self.ik_ctrls[0],
            ln="foot_roll",
            at="float",
            min=0,
            max=1,
            dv=defult_foot_roll_value,
            k=True,
        )
        defult_foot_bank_value = self.data["parameters"].get("bank", 0.0)
        pm.addAttr(
            self.ik_ctrls[0],
            ln="foot_bank",
            at="float",
            min=0,
            max=1,
            dv=defult_foot_bank_value,
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
        # pylint: disable-next=assignment-from-no-return
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
        # pylint: disable-next=assignment-from-no-return
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
        # pylint: disable-next=assignment-from-no-return
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

    def _create_reverse_foot_loc(self):
        loc_transform = [
            self.side_inner_transform,
            self.side_outer_transform,
            self.heel_transform,
            self.eff_transform,
            self.toe_transform,
        ]
        loc_names = ["sideInner", "sideOuter", "heel", "eff", "toe"]
        for i, t in enumerate(loc_transform):
            # pylint: disable-next=assignment-from-no-return
            loc = pm.spaceLocator(n=self._get_name(loc_names[i], "pivot"))
            pm.xform(loc, ws=1, m=t)
            self.reverse_foot_locs.append(loc)
            if i > 0:
                pm.parent(loc, self.reverse_foot_locs[i - 1])
            else:
                pm.parent(loc, self.ik_ctrls[0])
                # loc.v.set(0)
        # pylint: disable-next=assignment-from-no-return
        rot_loc = pm.spaceLocator(n=self._get_name("toeFK", "pivot"))
        pm.xform(rot_loc, ws=1, m=self.toe_transform)
        pm.parent(rot_loc, self.reverse_foot_locs[-2])
        print(self.reverse_foot_locs[-2])
        self.reverse_foot_locs.append(rot_loc)
        # loc.v.set(0)
