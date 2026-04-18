import bpy
from mathutils import Matrix, Vector, Euler


def _format_vector(value):
    return ",".join([f"{component:.6f}" for component in value])


def _format_quaternion(value):
    return ",".join([f"{component:.6f}" for component in value])


def _format_matrix(value):
    return ";".join([
        ",".join([f"{entry:.6f}" for entry in row])
        for row in value
    ])


def parse_net_to_bpy_matrix(matrix):
    '''Casts a .NET matrix directly to a Blender matrix'''
    return Matrix((
        (matrix.M11, matrix.M21, matrix.M31, matrix.M41),
        (matrix.M12, matrix.M22, matrix.M32, matrix.M42),
        (matrix.M13, matrix.M23, matrix.M33, matrix.M43),
        (matrix.M14, matrix.M24, matrix.M34, matrix.M44)
    ))


def net_to_bpy_matrix(matrix, debug_logger=None, debug_label: str | None = None):
    '''Converts a .NET matrix to a Blender matrix'''

    # in the current fake module version (3.4), the decompose function is incorrectly declared
    incoming_matrix = parse_net_to_bpy_matrix(matrix)
    position, rotation, scale = incoming_matrix.decompose()  # pylint: disable=assignment-from-no-return

    new_pos = Vector((position.x, -position.z, position.y))
    new_scale = Vector((scale.x, scale.z, scale.y))

    euler_rotation: Euler = rotation.to_euler('XZY')
    new_euler_rotation = Euler(
        (euler_rotation.x, -euler_rotation.z, euler_rotation.y))

    # It is not declared incorrectly here, but still throws the same error. Weird.
    new_rotation = new_euler_rotation.to_quaternion() # pylint: disable=assignment-from-no-return
    final_matrix = Matrix.LocRotScale(new_pos, new_rotation, new_scale)

    if debug_logger is not None and debug_logger.enabled:
        label = "none" if debug_label is None else debug_label.replace(" ", "_")
        debug_logger.emit(
            "PARITY_MATRIX_BLENDERIO",
            label=label,
            stage="incoming_net_matrix",
            matrix=_format_matrix(incoming_matrix))
        debug_logger.emit(
            "PARITY_MATRIX_BLENDERIO",
            label=label,
            stage="decomposed_prs",
            position=_format_vector(position),
            rotation_quaternion=_format_quaternion(rotation),
            scale=_format_vector(scale))
        debug_logger.emit(
            "PARITY_MATRIX_BLENDERIO",
            label=label,
            stage="rotation_to_euler_xzy",
            euler=_format_vector(euler_rotation))
        debug_logger.emit(
            "PARITY_MATRIX_BLENDERIO",
            label=label,
            stage="axis_remapped_values",
            position=_format_vector(new_pos),
            euler=_format_vector(new_euler_rotation),
            scale=_format_vector(new_scale))
        debug_logger.emit(
            "PARITY_MATRIX_BLENDERIO",
            label=label,
            stage="final_blender_matrix",
            matrix=_format_matrix(final_matrix))

    return final_matrix


def net_to_bpy_matrices(matrices, debug_logger=None, debug_label_prefix: str | None = None):
    '''Converts a list of .NET matrices to Blender matrices'''
    output = []
    for index, matrix in enumerate(matrices):
        label = None
        if debug_label_prefix is not None:
            label = f"{debug_label_prefix}_{index}"
        output.append(net_to_bpy_matrix(matrix, debug_logger, label))
    return output


def get_bone_transforms(bone: bpy.types.PoseBone):
    local_matrix = bone.bone.matrix_local

    if bone.parent is not None:
        parent_matrix = bone.parent.bone.matrix_local.inverted()
        local_matrix = parent_matrix @ local_matrix

    position_offset, local_rotation, _ = local_matrix.decompose()
    rotation_matrix = local_rotation.to_matrix().to_4x4()

    return position_offset, rotation_matrix
