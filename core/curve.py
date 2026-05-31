import json
import os
import math

import maya.cmds as mc
import maya.api.OpenMaya as om

DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "curve_shape.json"
)


_AXIS_VEC = {
    "x": om.MVector(1, 0, 0),
    "y": om.MVector(0, 1, 0),
    "z": om.MVector(0, 0, 1),
}


def _rotate_matrix(axis="x", angle=0.0):
    if not angle:
        return om.MMatrix()
    rad = math.radians(angle)
    return om.MQuaternion(rad, _AXIS_VEC[axis]).asMatrix()


def _shape_to_data(shape):
    sel = om.MSelectionList()
    sel.add(shape)
    fn = om.MFnNurbsCurve(sel.getDagPath(0))

    form_map = {1: "open", 2: "closed", 3: "periodic"}
    return {
        "degree": fn.degree,
        "form": form_map.get(fn.form, "open"),
        "knots": list(fn.knots()),
        "points": [[p.x, p.y, p.z] for p in fn.cvPositions(om.MSpace.kObject)],
    }


def export_shape(transform):
    shapes = (
        mc.listRelatives(str(transform), shapes=True, type="nurbsCurve", fullPath=True)
        or []
    )
    if not shapes:
        raise ValueError(f"No nurbsCurve shapes under {transform}")
    return {"shapes": [_shape_to_data(s) for s in shapes]}


def export_to_library(name, transform, path):

    lib = {}
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            lib = json.load(f)
    lib[name] = export_shape(transform)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lib, f, indent=2)
    print(f"Exported '{name}' ({len(lib[name]['shapes'])} shape(s)) -> {path}")


def build_shape(parent, data, rotate_axis="x", rotate_angle=0.0, size=1.0):
    data = data[0]
    degree = data["degree"]
    knots = data["knots"]
    periodic = data["form"] == "periodic"

    mtx = _rotate_matrix(rotate_axis, rotate_angle)
    points = [list(om.MPoint([c * size for c in p]) * mtx)[:3] for p in data["points"]]

    crv = mc.curve(p=points, k=knots, d=degree, per=periodic)
    shape = mc.listRelatives(crv, shapes=True, fullPath=True)[0]
    mc.parent(shape, str(parent), shape=True, relative=True)
    mc.delete(crv)
    return shape
