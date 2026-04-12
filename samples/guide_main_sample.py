import sys
import importlib

PATH = r"C:/Users/USER/Desktop/scripts"
sys.path.append(PATH)

import pinky_rig.builder.guide as main

importlib.reload(main)

test = main.Main()
test.add_parameter("jnt_num", 90)
print(test.parameter_names)
