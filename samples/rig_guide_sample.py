import sys
import importlib
import pymel.core as pm

PATH = r"C:/Users/USER/Desktop/scripts"
sys.path.append(PATH)

import pinky_rig.builder.guide as guide
import pinky_rig.components.arm_01.guide as arm_guide

importlib.reload(guide)
importlib.reload(arm_guide)

GUIDE_REGISTRY = {"ArmGuide": arm_guide.ArmGuide}

root = guide.RigGuide("Pinky")
a = arm_guide.ArmGuide("Arm")
b = arm_guide.ArmGuide("Arm")
root.add_component(a)
root.add_component(b, "Arm_C0_wrist_guide")
root.draw()
data = root.serialize()
pm.delete(root.grp_name)

root_b = guide.RigGuide()
root_b.deserialize(data, GUIDE_REGISTRY)
