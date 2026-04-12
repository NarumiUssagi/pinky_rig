import sys
import importlib

PATH = r"C:/Users/USER/Desktop/scripts"
if PATH not in sys.path:
    sys.path.append(PATH)

from pinky_rig.builder import guide, rig
from pinky_rig.components.spine_01 import guide as spine_guide, rig as spine_rig
from pinky_rig.components.arm_01 import guide as arm_guide, rig as arm_rig

for mod in [rig, guide, spine_guide, spine_rig, arm_guide, arm_rig]:
    importlib.reload(mod)

GUIDE_REGISTRY = {
    "ArmGuide": arm_guide.ArmGuide,
    "SpineGuide": spine_guide.SpineGuide,
}

RIG_REGISTRY = {
    "ArmGuide": arm_rig.ArmRig,
    "SpineGuide": spine_rig.SpineRig,
}

root = guide.RigGuide("Pinky")
a = spine_guide.SpineGuide("Spine")
b = arm_guide.ArmGuide("Arm")
c = arm_guide.ArmGuide("Arm")
root.add_component(a)
root.add_component(b, parent="Spine:middle:0:chest")
root.add_component(c, parent="Spine:middle:0:spine")
root.draw()
data = root.serialize()

# root_b = guide.RigGuide('Pinky')
# root_b.deserialize(data, GUIDE_REGISTRY)

builder = rig.RigBuilder(root.naming_config, data, RIG_REGISTRY)
builder.build()
