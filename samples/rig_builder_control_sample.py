import sys
import importlib

PATH = r"C:/Users/USER/Desktop/scripts"
if PATH not in sys.path:
    sys.path.append(PATH)

from pinky_rig.builder import guide, rig
from pinky_rig.components.spine_01 import guide as spine_guide, rig as spine_rig
from pinky_rig.components.neck_01 import guide as neck_guide, rig as neck_rig
from pinky_rig.components.arm_01 import guide as arm_guide, rig as arm_rig
from pinky_rig.components.leg_01 import guide as leg_guide, rig as leg_rig
from pinky_rig.components.control_01 import guide as control_guide, rig as control_rig
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
    control_guide,
    control_rig,
    neck_guide,
    neck_rig,
    transform,
    joint,
]:
    importlib.reload(mod)

GUIDE_REGISTRY = {
    "ArmGuide": arm_guide.ArmGuide,
    "SpineGuide": spine_guide.SpineGuide,
    "NeckGuide": neck_guide.NeckGuide,
    "LegGuide": leg_guide.LegGuide,
    "ControlGuide": control_guide.ControlGuide,
}

RIG_REGISTRY = {
    "ArmGuide": arm_rig.ArmRig,
    "SpineGuide": spine_rig.SpineRig,
    "NeckGuide": neck_rig.NeckRig,
    "LegGuide": leg_rig.LegRig,
    "ControlGuide": control_rig.ControlRig,
}

# 1. Build guides
root = guide.RigGuide("Pinky")
spine = spine_guide.SpineGuide("Spine")
clavicle = control_guide.ControlGuide("Clavicle", "right")
arm = arm_guide.ArmGuide("Arm", "right")
leg = leg_guide.LegGuide("Leg", "right")
neck = neck_guide.NeckGuide("Neck")
root.add_component(spine)
neck.set_parameter_value("segment", 0)
spine.set_parameter_value("segment", 2)
root.add_component(neck, parent="Spine:middle:0:chest")
root.add_component(clavicle, parent="Spine:middle:0:chest")
root.add_component(arm, parent="Clavicle:right:0:root")
root.add_component(leg, parent="Spine:middle:0:root")
root.draw()

# 2. Mirror guides
root.mirror_all(registry=GUIDE_REGISTRY)

# 3. Serialize guide data
data = root.serialize()

# 4. Build rig from data
builder = rig.RigBuilder(root.naming_config, data, RIG_REGISTRY)
builder.build()
