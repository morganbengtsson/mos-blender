import bpy
import os


def library_path(blender_object):
    library = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0] + '/'
    if blender_object.library:
        library, file_extension = os.path.splitext(bpy.path.basename(blender_object.library.filepath))
        library = library + '/'
    return library


def mat_to_list(mat):
    transform_list = list()
    for row in mat.col:
        transform_list.extend(list(row))
    return transform_list