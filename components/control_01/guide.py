"""
ControlGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class ControlGuide(Guide):
    def __init__(self, name="control", side="right", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = ["root"]
        self.save_helpers = ["upv", "eff"]
        self.root = None
        self.upv = None
        self.eff = None

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (-2, 0, 0))
        upv_mtx = transform.get_offset_matrix(self.parent, (-2, 0, -5))
        eff_mtx = transform.get_offset_matrix(self.parent, (-3, 0, 0))

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        self.upv = self.add_loc(
            self._get_name("upv"),
            parent=self.root,
            position=upv_mtx,
        )
        self.eff = self.add_loc(
            self._get_name("eff"),
            parent=self.root,
            position=eff_mtx,
        )
