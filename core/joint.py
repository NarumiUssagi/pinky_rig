"""
Joint
"""

import pymel.core as pm


def create_joint_chain(transform, names=None, parent=None, chain=True):
    jnts = []

    if isinstance(transform, dict):
        items = list(transform.items())
    else:
        items = [(i, t) for i, t in enumerate(transform)]

    for i, (key, mtx) in enumerate(items):
        pm.select(cl=True)
        name = names[i] if names else str(key)
        jnt = pm.joint(n=name)

        if chain:
            current_parent = parent if i == 0 else jnts[-1]
        else:
            current_parent = parent
        if current_parent:
            pm.parent(jnt, current_parent)

        pm.xform(jnt, a=True, ws=True, m=mtx)
        pm.makeIdentity(jnt, a=True, r=True)
        jnt.segmentScaleCompensate.set(0)
        jnts.append(jnt)

    return jnts
