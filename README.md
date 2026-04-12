# Pinky Rig

A modular auto-rigging framework for Maya, inspired by mGear's Shifter architecture. Guides are defined in the scene, serialized to JSON, and rigs are built from that data without requiring live scene guides.

## Requirements

- Maya 2023+
- PyMEL
- Python 3.9+ (included with Maya 2023)

## Installation

Add the parent directory of `pinky_rig` to your Maya script path:

```python
import sys
sys.path.append("path/to/your/scripts")
```

## Quick Start

```python
from pinky_rig.components.spine_01.guide import SpineGuide
from pinky_rig.components.arm_01.guide import ArmGuide
from pinky_rig.components.arm_01.rig import ArmRig
from pinky_rig.components.spine_01.rig import SpineRig
from pinky_rig.builder.guide import RigGuide
from pinky_rig.builder.rig import RigBuilder

# 1. Build guides
rig_guide = RigGuide(name="character")
spine = SpineGuide(name="spine", side="middle")
arm = ArmGuide(name="arm", side="left")

rig_guide.add_component(spine)
rig_guide.add_component(arm, parent="spine:middle:0:chest")
rig_guide.draw()

# 2. Serialize guide data
data = rig_guide.serialize()

# 3. Build rig from data
registry = {"SpineGuide": SpineRig, "ArmGuide": ArmRig}
config = rig_guide.naming_config
builder = RigBuilder(config=config, data=data, registry=registry)
builder.build()
```

## Project Structure

```
pinky_rig/
├── builder/          # Core framework classes
│   ├── main.py       #   Parameter system base class
│   ├── guide.py      #   Guide base class and RigGuide manager
│   ├── rig.py        #   Rig base class and RigBuilder orchestrator
│   └── naming.py     #   Naming convention system
├── components/       # Rigging components
│   ├── arm_01/       #   FK/IK arm with blend
│   └── spine_01/     #   FK spine chain
├── core/             # Shared utilities
│   ├── joint.py      #   Joint creation helpers
│   ├── control.py    #   Control curve creation
│   └── transform.py  #   Matrix and transform utilities
├── config/
│   └── naming.json   #   Default naming configuration
└── samples/          #   Example scripts (WIP)
```

## Author
Pinky Rig is developed by Pinky Bunny.

## Current Status

Work in progress. Currently implemented:

- Guide system with full serialize/deserialize round-trip
- Data-driven rig building from JSON (no live guides required)
- Phase-based build pipeline (objects → attributes → operators → relations)
- Components: arm (FK/IK blend), spine (FK)
