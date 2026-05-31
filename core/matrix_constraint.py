import math
import maya.cmds as mc
import maya.api.OpenMaya as om


def get_dag_path(node):
    if not node or not mc.objExists(str(node)):
        raise ValueError(f"Node does not exist: {node}")
    sel = om.MSelectionList()
    sel.add(str(node))
    return sel.getDagPath(0)


def get_local_offset(driver=None, driven=None):
    driver_wm = get_dag_path(driver).inclusiveMatrix()
    driven_wm = get_dag_path(driven).inclusiveMatrix()

    return driven_wm * driver_wm.inverse()


def matrix_parent_constraint(
    driver,
    driven,
    name="",
    maintain_offset=True,
    skip_translate=None,
    skip_rotate=None,
    skip_scale=None,
):
    if not name:
        name = f"{driver}_to_{driven}"

    skip_translate = skip_translate or []
    skip_rotate = skip_rotate or []
    skip_scale = skip_scale or []

    is_joint = mc.nodeType(str(driven)) == "joint"

    # Check for existing connections
    for axis in ("x", "y", "z"):
        for attr_prefix, skip in (
            ("t", skip_translate),
            ("r", skip_rotate),
            ("s", skip_scale),
        ):
            if axis in skip:
                continue
            full = f"{driven}.{attr_prefix}{axis}"
            existing = mc.listConnections(
                full, source=True, destination=False, plugs=True
            )
            if existing:
                raise RuntimeError(f"{full} already connected from {existing[0]}")

    # Core matrix chain: offset * driverWM * drivenPIM
    mmx = mc.createNode("multMatrix", n=name + "_mmx")
    if maintain_offset:
        mc.setAttr(
            f"{mmx}.matrixIn[0]",
            list(get_local_offset(driver, driven)),
            type="matrix",
        )
    mc.connectAttr(f"{driver}.worldMatrix[0]", f"{mmx}.matrixIn[1]", f=True)
    mc.connectAttr(f"{driven}.parentInverseMatrix[0]", f"{mmx}.matrixIn[2]", f=True)

    # Decompose for translate / scale (and rotate if not joint)
    dmx = mc.createNode("decomposeMatrix", n=name + "_dmx")
    mc.connectAttr(f"{mmx}.matrixSum", f"{dmx}.inputMatrix", f=True)
    mc.connectAttr(f"{driven}.rotateOrder", f"{dmx}.inputRotateOrder", f=True)

    # For joints: peel jointOrient off the local matrix to get pure rotate
    rot_dmx = dmx
    if is_joint and any(a not in skip_rotate for a in ("x", "y", "z")):
        jo = mc.getAttr(f"{driven}.jointOrient")[0]
        jo_inv = (
            om.MEulerRotation(
                math.radians(jo[0]), math.radians(jo[1]), math.radians(jo[2])
            )
            .asMatrix()
            .inverse()
        )
        rot_mmx = mc.createNode("multMatrix", n=name + "_rotate_mmx")
        mc.connectAttr(f"{mmx}.matrixSum", f"{rot_mmx}.matrixIn[0]", f=True)
        mc.setAttr(f"{rot_mmx}.matrixIn[1]", list(jo_inv), type="matrix")

        rot_dmx = mc.createNode("decomposeMatrix", n=name + "_rotate_dmx")
        mc.connectAttr(f"{rot_mmx}.matrixSum", f"{rot_dmx}.inputMatrix", f=True)
        mc.connectAttr(f"{driven}.rotateOrder", f"{rot_dmx}.inputRotateOrder", f=True)

    for axis in ("x", "y", "z"):
        A = axis.upper()
        if axis not in skip_translate:
            mc.connectAttr(f"{dmx}.outputTranslate{A}", f"{driven}.t{axis}", f=True)
        if axis not in skip_rotate:
            mc.connectAttr(f"{rot_dmx}.outputRotate{A}", f"{driven}.r{axis}", f=True)
        if axis not in skip_scale:
            mc.connectAttr(f"{dmx}.outputScale{A}", f"{driven}.s{axis}", f=True)


def matrix_aim_constraint(
    driven,
    driver,
    up_object,
    name="",
    primary_axis=(1, 0, 0),
    secondary_axis=(0, 1, 0),
    maintain_offset=True,
    extra_offset_euler=None,
):
    is_joint = mc.nodeType(str(driven)) == "joint"

    if not name:
        name = f"{driver}_to_{driven}"

    # --- aimMatrix ---
    aim = mc.createNode("aimMatrix", n=f"{name}_aim")
    mc.setAttr(f"{aim}.primaryInputAxis", *primary_axis, type="double3")
    mc.setAttr(f"{aim}.secondaryInputAxis", *secondary_axis, type="double3")
    mc.setAttr(f"{aim}.primaryMode", 1)
    mc.setAttr(f"{aim}.secondaryMode", 2)

    mc.connectAttr(f"{driven}.parentMatrix[0]", f"{aim}.inputMatrix", f=True)
    mc.connectAttr(f"{driver}.worldMatrix[0]", f"{aim}.primaryTargetMatrix", f=True)
    mc.connectAttr(
        f"{up_object}.worldMatrix[0]", f"{aim}.secondaryTargetMatrix", f=True
    )

    # --- offset (computed before aim is wired downstream) ---
    offset_matrix = om.MMatrix()
    if maintain_offset:
        aim_out = om.MMatrix(mc.getAttr(f"{aim}.outputMatrix"))
        driven_world = om.MMatrix(mc.getAttr(f"{driven}.worldMatrix[0]"))
        offset_matrix = driven_world * aim_out.inverse()

    if extra_offset_euler:
        rx, ry, rz = (math.radians(v) for v in extra_offset_euler)
        offset_matrix = om.MEulerRotation(rx, ry, rz).asMatrix() * offset_matrix

    # --- single multMatrix: offset * aim * parentInverse [* jointOrient.inv] ---
    mmx = mc.createNode("multMatrix", n=f"{name}_mmx")
    mc.setAttr(f"{mmx}.matrixIn[0]", list(offset_matrix), type="matrix")
    mc.connectAttr(f"{aim}.outputMatrix", f"{mmx}.matrixIn[1]", f=True)
    mc.connectAttr(f"{driven}.parentInverseMatrix[0]", f"{mmx}.matrixIn[2]", f=True)

    if is_joint:
        jo = mc.getAttr(f"{driven}.jointOrient")[0]
        jo_inv = (
            om.MEulerRotation(
                math.radians(jo[0]), math.radians(jo[1]), math.radians(jo[2])
            )
            .asMatrix()
            .inverse()
        )
        mc.setAttr(f"{mmx}.matrixIn[3]", list(jo_inv), type="matrix")

    # --- decompose rotate only ---
    dmx = mc.createNode("decomposeMatrix", n=f"{name}_dmx")
    mc.connectAttr(f"{mmx}.matrixSum", f"{dmx}.inputMatrix", f=True)
    mc.connectAttr(f"{driven}.rotateOrder", f"{dmx}.inputRotateOrder", f=True)

    for axis in "XYZ":
        mc.connectAttr(f"{dmx}.outputRotate{axis}", f"{driven}.r{axis.lower()}", f=True)

    return {"aim": aim, "mmx": mmx, "dmx": dmx}


def matrix_blend_constraint(
    driver_a,
    driver_b,
    driven,
    value=1.0,
    driver_attr=None,
    name="",
    skip_translate=None,
    skip_rotate=None,
    skip_scale=None,
    blend_translate=True,
    blend_rotate=True,
    blend_scale=True,
    maintain_offset=True,
):
    is_joint = mc.nodeType(str(driven)) == "joint"
    if not name:
        name = f"{driver_a}_{driver_b}_to_{driven}"

    skip_translate = skip_translate or []
    skip_rotate = skip_rotate or []
    skip_scale = skip_scale or []

    # --- driver matrices → local space ---
    driver_a_local = mc.createNode("multMatrix", n=f"{name}_driverA_local_mmx")
    driver_b_local = mc.createNode("multMatrix", n=f"{name}_driverB_local_mmx")
    mc.connectAttr(f"{driver_a}.worldMatrix[0]", f"{driver_a_local}.matrixIn[0]")
    mc.connectAttr(f"{driver_b}.worldMatrix[0]", f"{driver_b_local}.matrixIn[0]")
    mc.connectAttr(f"{driven}.parentInverseMatrix[0]", f"{driver_a_local}.matrixIn[1]")
    mc.connectAttr(f"{driven}.parentInverseMatrix[0]", f"{driver_b_local}.matrixIn[1]")

    # --- blendMatrix: input = driver_a, target[0] = driver_b ---
    bmx = mc.createNode("blendMatrix", n=f"{name}_bmx")
    mc.connectAttr(f"{driver_a_local}.matrixSum", f"{bmx}.inputMatrix")

    # Pick matrix
    if not (blend_translate and blend_rotate and blend_scale):
        pmx = mc.createNode("pickMatrix", n=f"{name}_pmx")
        mc.connectAttr(f"{driver_b_local}.matrixSum", f"{pmx}.inputMatrix")
        mc.setAttr(f"{pmx}.useTranslate", blend_translate)
        mc.setAttr(f"{pmx}.useRotate", blend_rotate)
        mc.setAttr(f"{pmx}.useScale", blend_scale)
        mc.connectAttr(f"{pmx}.outputMatrix", f"{bmx}.target[0].targetMatrix", f=True)
    else:
        mc.connectAttr(f"{driver_b_local}.matrixSum", f"{bmx}.target[0].targetMatrix")
    # Set value
    mc.setAttr(f"{bmx}.target[0].weight", value)

    # --- core chain: offset * blend_output (both local) ---
    # NOTE: weights set above, so bmx.outputMatrix now reflects the build-time blend.
    mmx = mc.createNode("multMatrix", n=f"{name}_mmx")
    if maintain_offset:
        blend_mtx = om.MMatrix(mc.getAttr(f"{bmx}.outputMatrix"))
        driven_local = om.MMatrix(mc.getAttr(f"{driven}.matrix"))
        offset = driven_local * blend_mtx.inverse()
        mc.setAttr(f"{mmx}.matrixIn[0]", list(offset), type="matrix")
    mc.connectAttr(f"{bmx}.outputMatrix", f"{mmx}.matrixIn[1]", f=True)

    # --- decompose for t / s (and r if not joint) ---
    dmx = mc.createNode("decomposeMatrix", n=f"{name}_dmx")
    mc.connectAttr(f"{mmx}.matrixSum", f"{dmx}.inputMatrix", f=True)
    mc.connectAttr(f"{driven}.rotateOrder", f"{dmx}.inputRotateOrder", f=True)

    # --- joint: peel jointOrient off rotate (reads mmx, includes offset) ---
    rot_dmx = dmx
    if is_joint and any(a not in skip_rotate for a in ("x", "y", "z")):
        jo = mc.getAttr(f"{driven}.jointOrient")[0]
        jo_inv = (
            om.MEulerRotation(
                math.radians(jo[0]), math.radians(jo[1]), math.radians(jo[2])
            )
            .asMatrix()
            .inverse()
        )
        rot_mmx = mc.createNode("multMatrix", n=f"{name}_rotate_mmx")
        mc.connectAttr(f"{mmx}.matrixSum", f"{rot_mmx}.matrixIn[0]", f=True)
        mc.setAttr(f"{rot_mmx}.matrixIn[1]", list(jo_inv), type="matrix")
        rot_dmx = mc.createNode("decomposeMatrix", n=f"{name}_rotate_dmx")
        mc.connectAttr(f"{rot_mmx}.matrixSum", f"{rot_dmx}.inputMatrix", f=True)
        mc.connectAttr(f"{driven}.rotateOrder", f"{rot_dmx}.inputRotateOrder", f=True)

    # --- connect channels ---
    for axis in ("x", "y", "z"):
        A = axis.upper()
        if axis not in skip_translate:
            mc.connectAttr(f"{dmx}.outputTranslate{A}", f"{driven}.t{axis}", f=True)
        if axis not in skip_rotate:
            mc.connectAttr(f"{rot_dmx}.outputRotate{A}", f"{driven}.r{axis}", f=True)
        if axis not in skip_scale:
            mc.connectAttr(f"{dmx}.outputScale{A}", f"{driven}.s{axis}", f=True)

    # --- optional envelope driver (global multiplier on all channels) ---
    if driver_attr:
        if not mc.objExists(str(driver_attr)):
            raise ValueError(f"driver_attr does not exist: {driver_attr}")
        mc.connectAttr(str(driver_attr), f"{bmx}.envelope", f=True)

    return bmx
