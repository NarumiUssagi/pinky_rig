"""
ArmGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class LegGuide(Guide):
    def __init__(self, name="leg", side="right", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = ["root", "knee", "ankle", "toe", "toeEnd"]
        self.save_helpers = ["upv", "eff", "heel", "sideInner", "sideOuter"]
        self.root = None
        self.knee = None
        self.ankle = None
        self.toe = None
        self.toe_end = None
        self.upv = None
        self.eff = None
        self.heel = None
        self.side_inner = None
        self.side_outer = None
        self.pref_axis = "+z"

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("ifk_blend", 1.0, "float")
        self.add_parameter(" foot_roll", 0.0, "float")
        self.add_parameter(" foot_bank", 0.0, "float")

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (-2, -2, 0))
        knee_mtx = transform.get_offset_matrix(self.parent, (-2, -7, 0.5))
        ankle_mtx = transform.get_offset_matrix(self.parent, (-2, -12, 0))
        toe_mtx = transform.get_offset_matrix(self.parent, (-2, -12, 2))
        toe_end_mtx = transform.get_offset_matrix(self.parent, (-2, -12, 4))
        upv_mtx = transform.get_offset_matrix(self.parent, (-2, -2, 5))
        eff_mtx = transform.get_offset_matrix(self.parent, (-2, -13, 5))
        heel_mtx = transform.get_offset_matrix(self.parent, (-2, -13, -1))
        side_inner_mtx = transform.get_offset_matrix(self.parent, (-1, -13, 3))
        side_outer_mtx = transform.get_offset_matrix(self.parent, (-3, -13, 3))

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        self.knee = self.add_loc(
            self._get_name("knee"),
            parent=self.root,
            position=knee_mtx,
        )
        self.ankle = self.add_loc(
            self._get_name("ankle"),
            parent=self.knee,
            position=ankle_mtx,
        )
        self.toe = self.add_loc(
            self._get_name("toe"),
            parent=self.ankle,
            position=toe_mtx,
        )
        self.toe_end = self.add_loc(
            self._get_name("toeEnd"),
            parent=self.toe,
            position=toe_end_mtx,
        )
        self.upv = self.add_loc(
            self._get_name("upv"),
            parent=self.root,
            position=upv_mtx,
        )
        self.eff = self.add_loc(
            self._get_name("eff"),
            parent=self.toe_end,
            position=eff_mtx,
        )
        self.heel = self.add_loc(
            self._get_name("heel"),
            parent=self.ankle,
            position=heel_mtx,
        )
        self.side_inner = self.add_loc(
            self._get_name("sideInner"),
            parent=self.ankle,
            position=side_inner_mtx,
        )
        self.side_outer = self.add_loc(
            self._get_name("sideOuter"),
            parent=self.ankle,
            position=side_outer_mtx,
        )
