"""
Control
"""

import pymel.core as pm


def create_control(
    name,
    offset_name,
    target_matrix=None,
    target_position=None,
    shape="circle",
    parent=None,
):
    if shape == "circle":
        ctrl = pm.circle(ch=False, n=name, nr=(1, 0, 0))[0]
    else:
        ctrl = pm.circle(ch=False, n=name, nr=(1, 0, 0))[0]

    # pylint: disable-next=assignment-from-no-return
    offset_grp = pm.group(ctrl, n=offset_name)

    if target_matrix:
        pm.xform(offset_grp, a=True, ws=True, m=target_matrix)

    if target_position:
        pm.xform(offset_grp, a=True, ws=True, t=target_position)

    if parent:
        pm.parent(offset_grp, parent)

    return offset_grp, ctrl
