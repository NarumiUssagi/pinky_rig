"""
EyeGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class EyeGuide(Guide):
    def __init__(self, name="eye", side="right", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = ["root"]
        self.save_helpers = ["aim"]
        self.root = None
        self.aim = None

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (-1, 0, 1))
        aim_mtx = transform.get_offset_matrix(self.parent, (-1, 0, 10))

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        self.aim = self.add_loc(
            self._get_name("aim"),
            parent=self.root,
            position=aim_mtx,
        )
