"""
ArmGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class LegGuide(Guide):
    def __init__(self, name="leg", side="right", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = ["root", "knee", "ankle"]
        self.save_helpers = ["upv", "eff"]
        self.root = None
        self.knee = None
        self.ankle = None
        self.upv = None
        self.eff = None
        self.pref_axis = "+z"

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("ifk_blend", 1.0, "float")

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (-2, -2, 0))
        knee_mtx = transform.get_offset_matrix(self.parent, (-2, -7, 0))
        ankle_mtx = transform.get_offset_matrix(self.parent, (-2, -12, 0))
        upv_mtx = transform.get_offset_matrix(self.parent, (-2, -2, 5))
        eff_mtx = transform.get_offset_matrix(self.parent, (-2, -12, 2))

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
        self.upv = self.add_loc(
            self._get_name("upv"),
            parent=self.root,
            position=upv_mtx,
        )
        self.eff = self.add_loc(
            self._get_name("eff"),
            parent=self.ankle,
            position=eff_mtx,
        )
