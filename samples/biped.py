import sys

PATH = r"C:/Users/USER/Desktop/scripts"
if PATH not in sys.path:
    sys.path.append(PATH)

import pymel.core as pm
from pinky_rig.builder import guide, rig, registry


def build_biped(root, gr):
    """Define biped component layout and parenting."""
    spine = gr["SpineGuide"]("Spine")
    spine.set_parameter_value("segment", 2)
    root.add_component(spine)

    neck = gr["NeckGuide"]("Neck")
    neck.set_parameter_value("segment", 0)
    root.add_component(neck, parent="Spine:middle:0:chest")

    # Eyes
    eye = gr["EyeGuide"]("Eye")
    eye_master = gr["ControlGuide"]("EyeMaster")
    eye.set_parameter_value("aim_master", "EyeMaster:middle:0:root")
    root.add_component(eye_master, parent="Neck:middle:0:head")
    root.add_component(eye, parent="Neck:middle:0:head")

    # Right arm + hand
    root.add_component(
        gr["ShoulderGuide"]("Clavicle", "right"), parent="Spine:middle:0:chest"
    )
    root.add_component(gr["ArmGuide"]("Arm", "right"), parent="Clavicle:right:0:root")
    _build_hand(root, gr, side="right")

    # Right leg
    root.add_component(gr["LegGuide"]("Leg", "right"), parent="Spine:middle:0:root")


def _build_hand(root, gr, side):
    """Hand: meta + 5 fingers, parented under wrist."""
    root.add_component(gr["MetaGuide"]("Meta", side), parent=f"Arm:{side}:0:wrist")
    root.add_component(gr["ChainGuide"]("Thumb", side), parent=f"Arm:{side}:0:wrist")
    finger_parents = {
        "Index": f"Meta:{side}:0:root",
        "Middle": f"Meta:{side}:0:meta0",
        "Ring": f"Meta:{side}:0:meta1",
        "Pinky": f"Meta:{side}:0:meta2",
    }
    for name, parent in finger_parents.items():
        root.add_component(gr["ChainGuide"](name, side), parent=parent)


# --- Pipeline ---
registry.reload_all()
GUIDE_REGISTRY, RIG_REGISTRY = registry.get_registries()

root = guide.RigGuide("Pinky")
build_biped(root, GUIDE_REGISTRY)
root.draw()

# Place guides that need manual offset
pm.setAttr("Thumb0_R_root_guide.t", (0, -1, 2))
pm.setAttr("Thumb0_R_root_guide.r", (50, 50, 0))

root.mirror_all(registry=GUIDE_REGISTRY)
data = root.serialize()

builder = rig.RigBuilder(root.naming_config, data, RIG_REGISTRY)
builder.build()
