"""
MetaRig Class
"""

import pymel.core as pm
import maya.api.OpenMaya as om

from ...builder.rig import Rig
from ...core import transform, joint, control


class MetaRig(Rig):
    def __init__(self, config=None, data=None, rig_builder=None):
        super().__init__(config=config, data=data, rig_builder=rig_builder)
        self.up_transform = self.helpers["upv"]
        self.segment = int(self.data["parameters"].get("segment"))
        self.meta_ctrl = None
        self.meta_offset = None
        self.meta_ctrl_grp = None
        self.meta_locs = []

    def add_objects(self):
        self._add_group()
        self._find_child_components()
        self._update_rotation()
        self._create_joints()
        self._create_meta_ctrl()

    def _update_rotation(self):
        children = self._find_child_components()
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
        up_vector = upv_point - root_point

        aim_axis = "+x"
        up_axis = "+y"

        if self.side == "left":
            aim_axis = "-x"
            up_axis = "-y"

        for i, pos in enumerate(positions):
            if i > 0:
                try:
                    child_pos = children[i - 1].transforms["root"][12:15]
                except KeyError:
                    keys = list(self.transforms.keys())
                    prev_flat = self.transforms[keys[i - 1]]  # flat 16-list
                    new_flat = list(prev_flat[:12]) + [pos.x, pos.y, pos.z, 1.0]
                    self.transforms[keys[i]] = new_flat
                    continue
            else:
                try:
                    child_pos = children["root"].transforms["root"][12:15]
                except KeyError:
                    continue

            child_point = om.MPoint(child_pos)
            mtx = transform.chain_orient_from_positions(
                [pos, child_point], up_vector, aim_axis=aim_axis, up_axis=up_axis
            )
            keys = list(self.transforms.keys())
            self.transforms[keys[i]] = list(mtx[0])

    def _find_child_components(self):
        children = {}
        for comp in self.builder.components:
            if comp is self:
                continue
            if not comp.parent or ":" not in comp.parent:
                continue
            # parent format "Meta:left:0:meta0"
            tokens = comp.parent.split(":")
            if len(tokens) < 4:
                continue
            name, side, index_str, desc = tokens[0], tokens[1], tokens[2], tokens[3]
            try:
                index = int(index_str)
            except ValueError:
                continue
            if name == self.name and side == self.side and index == self.index:
                if desc.startswith("meta"):
                    try:
                        meta_idx = int(desc[4:])
                        children[meta_idx] = comp
                    except ValueError:
                        continue
                elif desc == "root":
                    meta_idx = "root"
                    children[meta_idx] = comp
        return children

    def _create_joints(self):
        names = [self._get_name(g, self.config.get("joint")) for g in self.transforms]
        self.jnts = joint.create_joint_chain(
            self.transforms, names=names, parent=self.builder.joint_grp, chain=False
        )

    def _create_meta_ctrl(self):
        meta_ctrl_grp_name = self._get_name(
            self.name + "_meta", self.config.get("group")
        )
        self.meta_ctrl_grp = pm.group(n=meta_ctrl_grp_name, p=self.ctrl_grp, em=True)

        meta_ctrl_name = self._get_name("meta", self.config.get("control"))
        meta_offset_name = self._get_name("meta", self.config.get("offset"))

        self.meta_offset, self.meta_ctrl = control.create_control(
            meta_ctrl_name,
            meta_offset_name,
            target_matrix=self.transforms[f"meta{self.segment-1}"],
            parent=self.meta_ctrl_grp,
        )

        # Create rotate blend joint
        names = [self._get_name(g, "loc") for g in self.transforms]
        self.meta_locs = joint.create_joint_chain(
            self.transforms, names=names, parent=self.meta_ctrl_grp, chain=False
        )
        for i, loc in enumerate(self.meta_locs):
            loc.v.set(0)
            point_con = pm.pointConstraint(
                self.meta_offset, self.meta_ctrl, loc, mo=True
            )
            orient_con = pm.orientConstraint(
                self.meta_offset, self.meta_ctrl, loc, mo=True
            )
            orient_con.interpType.set(2)

            value = i / (len(self.meta_locs) - 1)
            point_tgts = pm.pointConstraint(point_con, q=1, wal=1)
            orient_tgts = pm.orientConstraint(orient_con, q=1, wal=1)
            point_tgts[1].set(value)
            point_tgts[0].set(1 - value)
            orient_tgts[1].set(value)
            orient_tgts[0].set(1 - value)

    def _default_parent_connection(self, target):
        if self.jnts:
            pm.parent(self.jnts, target)

        for grp in self._get_follow_parent_groups():
            if grp:
                pm.parentConstraint(target, grp, mo=True)
                pm.scaleConstraint(target, grp, mo=True)

    def _get_follow_parent_groups(self):
        return [self.meta_ctrl_grp]

    def add_operators(self):
        for loc, jnt in zip(self.meta_locs, self.jnts):
            pm.parentConstraint(loc, jnt, mo=True)
            pm.scaleConstraint(loc, jnt, mo=True)
