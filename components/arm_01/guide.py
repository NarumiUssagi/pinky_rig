"""
ArmGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class ArmGuide(Guide):
    def __init__(self, name="arm", side="middle", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = ["root", "elbow", "wrist"]
        self.save_helpers = ["upv", "eff"]
        self.root = None
        self.elbow = None
        self.wrist = None
        self.upv = None
        self.eff = None

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("ifk_blend", 0.0, "float")

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent)
        elbow_mtx = transform.get_offset_matrix(self.parent, (-5, 0, 0))
        wrist_mtx = transform.get_offset_matrix(self.parent, (-10, 0, 0))
        upv_mtx = transform.get_offset_matrix(self.parent, (-5, 5, 0))
        eff_mtx = transform.get_offset_matrix(self.parent, (-12.5, 0, 0))

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        self.elbow = self.add_loc(
            self._get_name("elbow"),
            parent=self.root,
            position=elbow_mtx,
        )
        self.wrist = self.add_loc(
            self._get_name("wrist"),
            parent=self.elbow,
            position=wrist_mtx,
        )
        self.upv = self.add_loc(
            self._get_name("upv"),
            parent=self.root,
            position=upv_mtx,
        )
        self.eff = self.add_loc(
            self._get_name("eff"),
            parent=self.wrist,
            position=eff_mtx,
        )
