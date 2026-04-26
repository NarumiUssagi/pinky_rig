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

        current_parent = parent if i == 0 else jnts[-1]
        if current_parent:
            pm.parent(jnt, current_parent)

        pm.xform(jnt, a=True, ws=True, m=mtx)
        pm.makeIdentity(jnt, a=True, r=True)
        jnt.segmentScaleCompensate.set(0)
        jnts.append(jnt)

    return jnts
