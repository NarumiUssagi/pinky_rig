# Pinky Rig

A modular auto-rigging framework for Maya, inspired by mGear's Shifter architecture and Cult of Rig's node-graph philosophy.

Guides are defined in the scene, serialized to JSON, and rigs are built from that data — the build step never requires live scene guides. Each component self-describes through a typed parameter system and registers itself through a component registry, so the whole rig is data-driven end to end.

## Features

- **Full serialize/deserialize round-trip** — guides export to a plain dict/JSON; rigs build from that data alone, with no dependency on live scene guides.
- **Component registry** — components are auto-discovered and resolved by type name; guide and rig classes are paired automatically.
- **Stage-based build pipeline** — every component runs through the same ordered phases: objects → attributes → operators → relations → connect.
- **Flat-string parent references** — components declare parents as `"Spine:middle:0:chest"`, resolved at draw/build time. Parents may not yet exist when declared, as long as draw order is correct.
- **Left/right mirroring** — any sided component can be authored once and mirrored across the YZ plane.
- **Procedural control sizing** — control curves are scaled by bone length, so proportions follow the guide layout automatically.
- **Side-based control coloring** — controls take left/right/middle colors by default, overridable per component.
- **Control shape library** — control curves are stored as JSON (degree / knots / form / object-space CVs); a matching exporter serializes any selected curve into the library.
- **Matrix-based constraints** — a standalone utility module provides matrix parent / aim / blend constraints built on `multMatrix` / `aimMatrix` / `blendMatrix`, with correct `jointOrient` handling.

## Components

| Component | Description |
|-----------|-------------|
| Spine     | FK spine chain (variable segments), includes the character Root control |
| Neck      | FK neck chain (variable segments) + head |
| Shoulder  | Clavicle |
| Arm       | FK/IK arm with blend |
| Leg       | FK/IK leg with reverse-foot setup (roll / bank / toe-tap / heel) |
| Meta      | Variable-segment metacarpal; child positions drive orientation |
| Chain     | Generic FK chain (used for fingers) |
| Eye       | Eye control + world-space aim control with shared aim master |
| Control   | Minimal pure-control component (used as aim master, etc.) |

A complete biped — spine, neck, eyes, both arms with full hands, and legs — builds from these components.

## Requirements

- Maya 2022+
- PyMEL
- Python 3 (included with Maya)

## Installation

Add the parent directory of `pinky_rig` to your Maya script path:

```python
import sys
sys.path.append("path/to/your/scripts")
```

## Quick Start

The full biped build lives in `biped.py`. The pipeline is:

```python
import pymel.core as pm
from pinky_rig.builder import guide, rig, registry

# 1. Discover all components
registry.reload_all()
GUIDE_REGISTRY, RIG_REGISTRY = registry.get_registries()

# 2. Author the guide layout
root = guide.RigGuide("Pinky")

spine = GUIDE_REGISTRY["SpineGuide"]("Spine")
spine.set_parameter_value("segment", 2)
root.add_component(spine)

arm = GUIDE_REGISTRY["ArmGuide"]("Arm", "right")
root.add_component(arm, parent="Spine:middle:0:chest")

# 3. Draw guides in the scene
root.draw()

# 4. (Optional) mirror sided components
root.mirror_all(registry=GUIDE_REGISTRY)

# 5. Serialize guide data
data = root.serialize()

# 6. Build the rig from data
builder = rig.RigBuilder(root.naming_config, data, RIG_REGISTRY)
builder.build()
```

Because step 6 only consumes `data`, the serialized JSON can be saved and rebuilt later without the original guides in the scene.

## Project Structure

```
pinky_rig/
├── builder/              # Core framework
│   ├── main.py           #   Typed parameter system (base class)
│   ├── guide.py          #   Guide base class + RigGuide manager
│   ├── rig.py            #   Rig base class + RigBuilder orchestrator
│   ├── naming.py         #   Naming convention system
│   └── registry.py       #   Component discovery + dev reload
├── components/           # Rigging components (each = guide.py + rig.py)
│   ├── spine_01/
│   ├── neck_01/
│   ├── shoulder_01/
│   ├── arm_01/
│   ├── leg_01/
│   ├── meta_01/
│   ├── chain_01/
│   ├── eye_01/
│   └── control_01/
├── core/                 # Shared utilities
│   ├── joint.py          #   Joint chain creation
│   ├── control.py        #   Control creation (shape library + size + color)
│   ├── curve.py          #   Curve shape export/build
│   ├── loader.py         #   JSON config loading
│   └── transform.py      #   Matrix / orientation utilities
├── config/
│   ├── naming.json       #   Naming configuration
│   └── curve_shape.json  #   Control shape library
└── biped.py              # Full biped build example
```

## Design Notes

- **Guide / Rig separation** — guide classes own scene authoring; rig classes consume serialized data. Rig building from JSON alone is the design goal, not an afterthought.
- **Parameter system** — `Main` provides a typed parameter dict shared by both guides and the rig container, so the same declaration drives Maya attribute creation and serialization.
- **Naming** — a single rule string + token config (`config/naming.json`) drives every node name, so naming conventions are data, not hard-coded.

## Author

Developed by Pinky Bunny.

## Status

Work in progress. The framework builds a complete biped today. Planned next:

- Facial components
- Consolidation of per-component rotation/orientation logic
- Optional Maya API 2.0 migration for core math (deferred until a performance need appears)
