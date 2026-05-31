"""Component registry & dev reload helpers."""

import importlib
from . import guide, rig
from ..core import transform, joint, control, matrix_constraint, loader, curve

# Single source of truth for all components
COMPONENT_MODULES = [
    "spine_01",
    "neck_01",
    "arm_01",
    "leg_01",
    "control_01",
    "shoulder_01",
    "eye_01",
    "chain_01",
    "meta_01",
]


def _import_component(mod_name):
    base = f"pinky_rig.components.{mod_name}"
    g = importlib.import_module(f"{base}.guide")
    r = importlib.import_module(f"{base}.rig")
    return g, r


def get_registries():
    """Return (guide_registry, rig_registry)."""
    guide_reg, rig_reg = {}, {}
    for mod_name in COMPONENT_MODULES:
        g_mod, r_mod = _import_component(mod_name)
        # Find the *Guide and *Rig class (one per module)
        guide_cls = next(
            c for n, c in vars(g_mod).items() if n.endswith("Guide") and n != "Guide"
        )
        rig_cls = next(
            c for n, c in vars(r_mod).items() if n.endswith("Rig") and n != "Rig"
        )
        guide_reg[guide_cls.__name__] = guide_cls
        rig_reg[guide_cls.__name__] = rig_cls
    return guide_reg, rig_reg


def reload_all():
    """For dev: reload framework + all components."""
    for mod in [
        transform,
        joint,
        control,
        guide,
        rig,
        matrix_constraint,
        loader,
        curve,
    ]:
        importlib.reload(mod)
    for mod_name in COMPONENT_MODULES:
        g_mod, r_mod = _import_component(mod_name)
        importlib.reload(g_mod)
        importlib.reload(r_mod)
