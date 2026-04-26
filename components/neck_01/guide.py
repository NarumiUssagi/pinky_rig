"""
NeckGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class NeckGuide(Guide):
    def __init__(self, name="neck", side="middle", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_transform = (
            ["root"] + [f"neck{i}" for i in range(self.segment)] + ["head"]
        )
        self.root = None
        self.necks = []
        self.head = None

    @property
    def segment(self):
        return int(self.get_parameter_value("segment"))

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("ifk_blend", 0.0, "float")
        self.add_parameter("segment", 1, "long")

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (0, 1, 0))
        head_mtx = transform.get_offset_matrix(self.parent, (0, 3, 0))

        self.save_transform = (
            ["root"] + [f"neck{i}" for i in range(self.segment)] + ["head"]
        )

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        for i in range(self.segment):
            y_value = 1 + (i + 1) * (2 / (self.segment + 1))
            spine_mtx = transform.get_offset_matrix(self.parent, (0, y_value, 0))
            parent_obj = self.root if i == 0 else self.necks[i - 1]
            spine = self.add_loc(
                self._get_name(f"neck{i}"),
                parent=parent_obj,
                position=spine_mtx,
            )
            self.necks.append(spine)

        if self.segment == 0:
            head_parent = self.root
        else:
            head_parent = self.necks[-1]
        self.head = self.add_loc(
            self._get_name("head"),
            parent=head_parent,
            position=head_mtx,
        )
