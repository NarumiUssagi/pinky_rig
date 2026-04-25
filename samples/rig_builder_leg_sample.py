import sys
import importlib

PATH = r"C:/Users/USER/Desktop/scripts"
if PATH not in sys.path:
    sys.path.append(PATH)

from pinky_rig.builder import guide, rig
from pinky_rig.components.spine_01 import guide as spine_guide, rig as spine_rig
from pinky_rig.components.arm_01 import guide as arm_guide, rig as arm_rig
from pinky_rig.components.leg_01 import guide as leg_guide, rig as leg_rig
import pinky_rig.core.transform as transform
import pinky_rig.core.joint as joint

for mod in [
    rig,
    guide,
    spine_guide,
    spine_rig,
    arm_guide,
    arm_rig,
    leg_guide,
    leg_rig,
    transform,
    joint,
]:
    importlib.reload(mod)

GUIDE_REGISTRY = {
    "ArmGuide": arm_guide.ArmGuide,
    "SpineGuide": spine_guide.SpineGuide,
    "LegGuide": leg_guide.LegGuide,
}

RIG_REGISTRY = {
    "ArmGuide": arm_rig.ArmRig,
    "SpineGuide": spine_rig.SpineRig,
    "LegGuide": leg_rig.LegRig,
}

# 1. Build guides

root = guide.RigGuide("Pinky")
spine = spine_guide.SpineGuide("Spine")
arm = arm_guide.ArmGuide("Arm", "right")
leg = leg_guide.LegGuide("Leg", "right")
root.add_component(spine)
root.add_component(arm, parent="Spine:middle:0:chest")
root.add_component(leg, parent="Spine:middle:0:root")
root.draw()

# 2. Mirror guides

mirror_components = [arm, leg]
for component in mirror_components:
    root.mirror_components(component, registry=GUIDE_REGISTRY)


# 3. Serialize guide data

data = root.serialize()

# 4. Build rig from data

builder = rig.RigBuilder(root.naming_config, data, RIG_REGISTRY)
builder.build()
