import bpy
import os


def library_directory(blender_object):
    library = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0] + '/'
    if blender_object.library:
        library, file_extension = os.path.splitext(blender_object.library.filepath)
        library = library + '/'
    return library
