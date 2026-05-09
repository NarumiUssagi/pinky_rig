import sys
import importlib
import pymel.core as pm

PATH = r"C:/Users/USER/Desktop/scripts"
if PATH not in sys.path:
    sys.path.append(PATH)

from pinky_rig.builder import guide, rig
from pinky_rig.components.spine_01 import guide as spine_guide, rig as spine_rig
from pinky_rig.components.neck_01 import guide as neck_guide, rig as neck_rig
from pinky_rig.components.arm_01 import guide as arm_guide, rig as arm_rig
from pinky_rig.components.leg_01 import guide as leg_guide, rig as leg_rig
from pinky_rig.components.control_01 import guide as control_guide, rig as control_rig
from pinky_rig.components.shoulder_01 import (
    guide as shoulder_guide,
    rig as shoulder_rig,
)
from pinky_rig.components.eye_01 import guide as eye_guide, rig as eye_rig
from pinky_rig.components.chain_01 import guide as chain_guide, rig as chain_rig
from pinky_rig.components.meta_01 import guide as meta_guide, rig as meta_rig
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
    shoulder_guide,
    shoulder_rig,
    neck_guide,
    neck_rig,
    chain_guide,
    chain_rig,
    eye_guide,
    eye_rig,
    meta_guide,
    meta_rig,
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
    "ShoulderGuide": shoulder_guide.ShoulderGuide,
    "ChainGuide": chain_guide.ChainGuide,
    "EyeGuide": eye_guide.EyeGuide,
    "MetaGuide": meta_guide.MetaGuide,
}

RIG_REGISTRY = {
    "ArmGuide": arm_rig.ArmRig,
    "SpineGuide": spine_rig.SpineRig,
    "NeckGuide": neck_rig.NeckRig,
    "LegGuide": leg_rig.LegRig,
    "ControlGuide": control_rig.ControlRig,
    "ShoulderGuide": shoulder_rig.ShoulderRig,
    "ChainGuide": chain_rig.ChainRig,
    "EyeGuide": eye_rig.EyeRig,
    "MetaGuide": meta_rig.MetaRig,
}

# 1. Build guides
root = guide.RigGuide("Pinky")
spine = spine_guide.SpineGuide("Spine")
clavicle = shoulder_guide.ShoulderGuide("Clavicle", "right")
arm = arm_guide.ArmGuide("Arm", "right")
meta = meta_guide.MetaGuide("Meta", "right")
thumb_finger = chain_guide.ChainGuide("Thumb", "right")
index_finger = chain_guide.ChainGuide("Index", "right")
middle_finger = chain_guide.ChainGuide("Middle", "right")
ring_finger = chain_guide.ChainGuide("Ring", "right")
pinky_finger = chain_guide.ChainGuide("Pinky", "right")
leg = leg_guide.LegGuide("Leg", "right")
neck = neck_guide.NeckGuide("Neck")
eye = eye_guide.EyeGuide("Eye")
eye_main = control_guide.ControlGuide("EyeMaster")
eye.set_parameter_value("aim_master", "EyeMaster:middle:0:root")
root.add_component(spine)
neck.set_parameter_value("segment", 0)
spine.set_parameter_value("segment", 2)
root.add_component(neck, parent="Spine:middle:0:chest")
root.add_component(eye, parent="Neck:middle:0:head")
root.add_component(eye_main, parent="Neck:middle:0:head")
root.add_component(clavicle, parent="Spine:middle:0:chest")
root.add_component(arm, parent="Clavicle:right:0:root")
root.add_component(leg, parent="Spine:middle:0:root")
root.add_component(meta, parent="Arm:right:0:wrist")
root.add_component(thumb_finger, parent="Arm:right:0:wrist")
root.add_component(index_finger, parent="Meta:right:0:root")
root.add_component(middle_finger, parent="Meta:right:0:meta0")
root.add_component(ring_finger, parent="Meta:right:0:meta1")
root.add_component(pinky_finger, parent="Meta:right:0:meta2")
root.draw()

# 2.5 Place guides
pm.setAttr("Thumb0_R_root_guide.t", (0, -1, 2))
pm.setAttr("Thumb0_R_root_guide.r", (50, 50, 0))

# 2. Mirror guides
root.mirror_all(registry=GUIDE_REGISTRY)

# 3. Serialize guide data
data = root.serialize()

# 4. Build rig from data
builder = rig.RigBuilder(root.naming_config, data, RIG_REGISTRY)
builder.build()
