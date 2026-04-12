"""
Joint
"""

import pymel.core as pm


def create_joint_chain(transform, names=None, parent=None):
    jnts = []

    if isinstance(transform, dict):
        items = list(transform.items())
    else:
        items = [(i, t) for i, t in enumerate(transform)]

    for i, (key, mtx) in enumerate(items):
        pm.select(cl=True)
        name = names[i] if names else str(key)

        # pylint: disable-next=assignment-from-no-return
        jnt = pm.joint(n=name)
        pm.xform(jnt, a=True, ws=True, m=mtx)

        current_parent = parent if i == 0 else jnts[-1]
        if current_parent:
            pm.parent(jnt, current_parent)

        jnts.append(jnt)

    return jnts
