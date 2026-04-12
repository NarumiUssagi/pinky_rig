import sys
import importlib
import pymel.core as pm

PATH = r"C:/Users/USER/Desktop/scripts"
sys.path.append(PATH)

import pinky_rig.builder.guide as guide
import pinky_rig.builder.naming as naming
import pinky_rig.components.arm_01.guide as arm
import pinky_rig.core.transform as transform

importlib.reload(guide)
importlib.reload(arm)
importlib.reload(naming)
importlib.reload(transform)

A = arm.ArmGuide("Test")
A.draw(pm.selected())

data = A.serialize()
print(data)
B = arm.ArmGuide("Test")
B.deserialize(data)
