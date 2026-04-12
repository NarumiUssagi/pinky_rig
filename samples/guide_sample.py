import sys
import importlib

PATH = r"C:/Users/USER/Desktop/scripts"
sys.path.append(PATH)

import pinky_rig.builder.guide as guide
import pinky_rig.builder.naming as naming
import pinky_rig.components.arm_01.guide as arm

importlib.reload(guide)
importlib.reload(arm)
importlib.reload(naming)

test = arm.ArmGuide("test")
test.add_objects()
