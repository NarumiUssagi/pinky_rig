"""
ChainGuide Class
"""

from ...builder.guide import Guide
from ...core import transform


class ChainGuide(Guide):
    def __init__(self, name="chain", side="middle", index=0, config=None):
        super().__init__(name=name, side=side, index=index, config=config)
        self.save_helpers = ["upv"]
        self.root = None
        self.chains = []
        self.upv = None

    @property
    def segment(self):
        return int(self.get_parameter_value("segment"))

    def _define_parameters(self):
        super()._define_parameters()
        self.add_parameter("segment", 2, "long")

    def add_objects(self):
        root_mtx = transform.get_offset_matrix(self.parent, (-1, 0, 0))

        self.save_transform = ["root"] + [f"chain{i}" for i in range(self.segment)]

        self.root = self.add_root(
            name=self._get_name("root"),
            parent=self.parent,
            position=root_mtx,
        )
        for i in range(self.segment):
            x_value = -1 - (i + 1)
            chain_mtx = transform.get_offset_matrix(self.parent, (x_value, 0, 0))
            parent_obj = self.root if i == 0 else self.chains[i - 1]
            chain = self.add_loc(
                self._get_name(f"chain{i}"),
                parent=parent_obj,
                position=chain_mtx,
            )
            self.chains.append(chain)

        # Helper
        upv_mtx = transform.get_offset_matrix(self.parent, (-1, 0, -3))

        self.upv = self.add_loc(
            self._get_name("upv"),
            parent=self.root,
            position=upv_mtx,
        )
