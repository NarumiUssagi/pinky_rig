"""
MetaGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class MetaGuide(Guide):
    def __init__(self, name="meta", side="middle", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_helpers = ["upv"]
        self.root = None
        self.metas = []
        self.upv = None

    @property
    def segment(self):
        return int(self.get_parameter_value("segment"))

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("segment", 3, "long")

    def add_objects(self):
        start = (self.segment) / 2
        root_mtx = transform.get_offset_matrix(self.parent, (-1, 0, start))

        self.save_transform = ["root"] + [f"meta{i}" for i in range(self.segment)]

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        for i in range(self.segment):
            z_value = start - (i + 1)
            meta_mtx = transform.get_offset_matrix(self.parent, (-1, 0, z_value))
            parent_obj = self.root if i == 0 else self.metas[i - 1]
            meta = self.add_loc(
                self._get_name(f"meta{i}"),
                parent=parent_obj,
                position=meta_mtx,
            )
            self.metas.append(meta)

        # Helper
        upv_mtx = transform.get_offset_matrix(self.parent, (-1, 3, start))

        self.upv = self.add_loc(
            self._get_name("upv"),
            parent=self.root,
            position=upv_mtx,
        )
