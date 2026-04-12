import sys
import importlib
import pymel.core as pm

PATH = r"C:/Users/USER/Desktop/scripts"
sys.path.append(PATH)

import pinky_rig.builder.guide as guide
import pinky_rig.builder.rig as rig
import pinky_rig.components.arm_01.guide as arm_guide
import pinky_rig.components.arm_01.rig as arm_rig
import pinky_rig.core.transform as transform
import pinky_rig.core.control as control

importlib.reload(rig)
importlib.reload(guide)
importlib.reload(arm_guide)
importlib.reload(arm_rig)
importlib.reload(transform)
importlib.reload(control)

RIG_REGISTRY = {"ArmGuide": arm_rig.ArmRig}

root = guide.RigGuide("Pinky")
a = arm_guide.ArmGuide("Arm")
root.add_component(a)
root.draw()
data = root.serialize()

builder = rig.RigBuilder(root.naming_config, data, RIG_REGISTRY)
builder.build()
