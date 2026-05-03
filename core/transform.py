"""
Transform
"""

import maya.cmds as mc
import maya.api.OpenMaya as om


def get_offset_matrix(parent_name=None, out_vec=None):
    out_m = om.MMatrix()
    if out_vec and len(out_vec) == 3:
        out_m = om.MMatrix(
            [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [out_vec[0], out_vec[1], out_vec[2], 1],
            ]
        )

    if parent_name:
        parent_name = str(parent_name)
    # pylint: disable-next=too-many-function-args
    if parent_name and mc.objExists(parent_name):

        sel = om.MSelectionList()
        sel.add(parent_name)
        dag_path = sel.getDagPath(0)
        parent_m = dag_path.inclusiveMatrix()
        output_m = out_m * parent_m
        return list(output_m)
    return list(out_m)


def find_pole_vector_position(positions, distance_multiplier=1.0, prefer_axis="+z"):
    if len(positions) != 3:
        return None

    a_pos = om.MPoint(positions[0])
    b_pos = om.MPoint(positions[1])
    c_pos = om.MPoint(positions[2])

    ac_vector = c_pos - a_pos
    ab_vector = b_pos - a_pos
    ac_normal = ac_vector.normal()
    ac_dis = ac_vector.length()

    t = ab_vector * ac_normal
    d_pos = a_pos + ac_normal * t
    db_vector = b_pos - d_pos
    db_dis = db_vector.length()

    if db_dis > 0.001:
        pv_dir = db_vector.normal()
    else:
        if prefer_axis == "+z":
            world_y = om.MVector(0, 0, 1)
        else:
            world_y = om.MVector(0, 0, -1)

        if abs(ac_normal * world_y) > 0.99:
            pv_dir = om.MVector(0, 1, 0)
        else:
            pv_dir = world_y
    result = b_pos + pv_dir * ac_dis * distance_multiplier
    return (result.x, result.y, result.z)


def chain_orient_from_positions(positions, up_vector, aim_axis="+x", up_axis="+y"):
    axis = ["x", "y", "z"]
    aim_negative = -1 if aim_axis.startswith("-") else 1
    up_negative = -1 if up_axis.startswith("-") else 1
    aim_axis = aim_axis[-1]
    up_axis = up_axis[-1]

    if aim_axis not in axis:
        raise ValueError(f"invalid aim_axis: {aim_axis}")
    if up_axis not in axis:
        raise ValueError(f"invalid up_axis: {up_axis}")
    if aim_axis == up_axis:
        raise ValueError("aim_axis and up_axis can't be the same")

    side_axis = list(set(axis) - {aim_axis, up_axis})[0]

    aim_idx = axis.index(aim_axis)
    up_idx = axis.index(up_axis)
    side_idx = axis.index(side_axis)

    result = []
    aim_vectors = []
    prev_side = om.MVector(1, 0, 0)

    for i, _ in enumerate(positions):
        if i < len(positions) - 1:
            aim_vector = (positions[i + 1] - positions[i]).normal()
        else:
            aim_vector = aim_vectors[-1] if aim_vectors else om.MVector(1, 0, 0)
        aim_vectors.append(aim_vector)

        side = (aim_vector ^ up_vector).normal()
        if side.length() < 0.001:
            side = prev_side
        side = side.normal()
        prev_side = side
        corrected_up = (side ^ aim_vector).normal()

        rows = [None, None, None]
        rows[aim_idx] = aim_vector * aim_negative
        rows[up_idx] = corrected_up * up_negative
        rows[side_idx] = side

        matrix = om.MMatrix(
            [
                rows[0].x,
                rows[0].y,
                rows[0].z,
                0,
                rows[1].x,
                rows[1].y,
                rows[1].z,
                0,
                rows[2].x,
                rows[2].y,
                rows[2].z,
                0,
                positions[i].x,
                positions[i].y,
                positions[i].z,
                1,
            ]
        )
        result.append(matrix)
    return result


def mirror_matrix_yz(matrix=None):
    if not matrix:
        return
    matrix = om.MMatrix(matrix)
    mirror_m = om.MMatrix(
        [
            [-1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    return matrix * mirror_m


def mirror_matrix_yz_translation_only(matrix=None):
    if not matrix:
        return
    m = list(matrix)
    m[12] = -m[12]
    return om.MMatrix(m)
