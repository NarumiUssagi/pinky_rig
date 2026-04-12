"""
Transform
"""

import pymel.core as pm


def get_offset_matrix(parent_name=None, out_vec=None):
    out_m = pm.datatypes.Matrix()
    if out_vec and len(out_vec) == 3:
        out_m.translate = out_vec
    if parent_name and pm.objExists(parent_name):
        parent_m = pm.datatypes.Matrix(pm.xform(parent_name, q=True, ws=True, m=True))
        output_m = out_m * parent_m
        return [item for sublist in output_m.get() for item in sublist]
    return [item for sublist in out_m.get() for item in sublist]


def find_pole_vector_position(positions, distance_multiplier=1.0):
    if len(positions) != 3:
        return None

    a_pos = pm.datatypes.Vector(positions[0])
    b_pos = pm.datatypes.Vector(positions[1])
    c_pos = pm.datatypes.Vector(positions[2])

    ac_vector = c_pos - a_pos
    ab_vector = b_pos - a_pos
    ac_normal = ac_vector.normal()
    ac_dis = ac_vector.length()

    t = ab_vector.dot(ac_normal)
    d_pos = a_pos + ac_normal * t
    db_vector = b_pos - d_pos
    db_dis = db_vector.length()

    if db_dis > 0.001:
        pv_dir = db_vector.normal()
    else:
        world_y = pm.datatypes.Vector(0, 1, 0)
        if abs(ac_normal.dot(world_y)) > 0.99:
            pv_dir = pm.datatypes.Vector(0, 0, 1)
        else:
            pv_dir = world_y

    return b_pos + pv_dir * ac_dis * distance_multiplier
