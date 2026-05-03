"""
ControlGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class ControlGuide(Guide):
    def __init__(self, name="control", side="middle", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = ["root"]
        self.save_helpers = []
        self.root = None

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (0, 0, 10))
        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
