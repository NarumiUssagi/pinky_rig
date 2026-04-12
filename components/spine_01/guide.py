"""
SpineGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class SpineGuide(Guide):
    def __init__(self, name="spine", side="middle", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = ["root", "spine", "chest"]
        self.root = None
        self.spine = None
        self.chest = None

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("ifk_blend", 0.0, "float")

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent)
        spine_mtx = transform.get_offset_matrix(self.parent, (0, 5, 0))
        chest_mtx = transform.get_offset_matrix(self.parent, (0, 10, 0))

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        self.spine = self.add_loc(
            self._get_name("spine"),
            parent=self.root,
            position=spine_mtx,
        )
        self.chest = self.add_loc(
            self._get_name("chest"),
            parent=self.spine,
            position=chest_mtx,
        )
