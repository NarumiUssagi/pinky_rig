"""
Control
"""

import pymel.core as pm


def create_control(
    name,
    offset_name,
    buffer_name=None,
    target_matrix=None,
    target_position=None,
    shape="circle",
    parent=None,
):
    if shape == "circle":
        ctrl = pm.circle(ch=False, n=name, nr=(1, 0, 0))[0]
    else:
        ctrl = pm.circle(ch=False, n=name, nr=(1, 0, 0))[0]

    if buffer_name:
        pm.group(ctrl, n=buffer_name, w=True)

    offset_grp = pm.group(n=offset_name, w=True)

    if target_matrix:
        pm.xform(offset_grp, a=True, ws=True, m=target_matrix)

    if target_position:
        pm.xform(offset_grp, a=True, ws=True, t=target_position)

    if parent:
        pm.parent(offset_grp, parent)

    return offset_grp, ctrl
