
"""bl_info = {
    "name":         "Mo materials format",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 1),
    "version":      (0, 0, 1),
    "location":     "File > Import-Export",
    "description":  "Export materials",
    "category":     "Import-Export"
}"""


import os
import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
from .mos import materials

class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.material"
    bl_label = "Mo material format"
    bl_options = {'PRESET'}
    filename_ext = ".material"

    def execute(self, context):
        materials.write(os.path.dirname(self.filepath))
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ExportMyFormat.bl_idname, text="Mo material format (.material)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
