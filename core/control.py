import maya.cmds as mc
from . import curve, loader


def create_control(
    name,
    offset_name,
    buffer_name=None,
    target_matrix=None,
    target_position=None,
    shape="circle",
    parent=None,
    color_rgb=None,
    lock_attrs=["v"],
    rotate_axis="x",
    rotate_angle=0.0,
    size=1.0,
):
    data = loader.load_config_from_json(curve.DEFAULT_CONFIG_PATH)
    ctrl = mc.createNode("transform", n=name)
    if shape in data.keys():
        curve.build_shape(ctrl, data[shape]["shapes"], rotate_axis, rotate_angle, size)
    else:
        curve.build_shape(
            ctrl, data["circle"]["shapes"], rotate_axis, rotate_angle, size
        )

    if buffer_name:
        buffer_grp = mc.group(ctrl, n=buffer_name, w=True)
        offset_grp = mc.group(buffer_grp, n=offset_name, w=True)
        mc.setAttr(f"{buffer_grp}.v", k=False)
    else:
        offset_grp = mc.group(ctrl, n=offset_name, w=True)
    mc.setAttr(f"{offset_grp}.v", k=False)

    if target_matrix:
        mc.xform(offset_grp, a=True, ws=True, m=target_matrix)
    elif target_position:
        mc.xform(offset_grp, a=True, ws=True, t=target_position)

    if parent:
        mc.parent(offset_grp, str(parent))

    if color_rgb:
        r, g, b = color_rgb
        mc.setAttr(f"{ctrl}.overrideEnabled", True)
        mc.setAttr(f"{ctrl}.overrideRGBColors", 1)
        mc.setAttr(f"{ctrl}.overrideColorRGB", r, g, b)

    if lock_attrs:
        for attr in lock_attrs:
            if mc.objExists(f"{ctrl}.{attr}"):
                mc.setAttr(f"{ctrl}.{attr}", l=True, k=False)

    return offset_grp, ctrl
