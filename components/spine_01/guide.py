"""
SpineGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class SpineGuide(Guide):
    def __init__(self, name="spine", side="middle", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.segment = int(self.get_parameter_value("segment"))
        self.save_transform = (
            ["root"] + [f"spine{i}" for i in range(self.segment)] + ["chest"]
        )
        self.root = None
        self.spines = []
        self.chest = None

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("ifk_blend", 0.0, "float")
        self.add_parameter("segment", 2, "long")

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (0, 13, 0))
        chest_mtx = transform.get_offset_matrix(self.parent, (0, 23, 0))

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        for i in range(self.segment):
            y_value = 13 + (i + 1) * (10 / (self.segment + 1))
            spine_mtx = transform.get_offset_matrix(self.parent, (0, y_value, 0))
            if i < 1:
                spine = self.add_loc(
                    self._get_name("spine" + str(i)),
                    parent=self.root,
                    position=spine_mtx,
                )
            else:
                spine = self.add_loc(
                    self._get_name("spine" + str(i)),
                    parent=self.spines[i - 1],
                    position=spine_mtx,
                )

            self.spines.append(spine)

        self.chest = self.add_loc(
            self._get_name("chest"),
            parent=self.spines[-1],
            position=chest_mtx,
        )
