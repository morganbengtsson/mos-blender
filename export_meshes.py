"""bl_info = {
    "name":         "Mo mesh format",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 1),
    "version":      (0, 0, 1),
    "location":     "File > Import-Export",
    "description":  "Export meshes",
    "category":     "Import-Export"
}"""


import os
import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
from .mos import meshes

class ExportMeshesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.mesh"
    bl_label = "Mo mesh format"
    bl_options = {'PRESET'}
    filename_ext = ".mesh"

    def execute(self, context):
        meshes.write(os.path.dirname(self.filepath), context.selected_objects)
        return {'FINISHED'}


def export_meshes_menu_func(self, context):
    self.layout.operator(ExportMeshesFormat.bl_idname, text="Mo mesh format (.mesh)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(export_meshes_menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(export_meshes_menu_func)

if __name__ == "__main__":
    register()
