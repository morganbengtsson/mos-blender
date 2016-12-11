import bpy
from bpy_extras.io_utils import ExportHelper
import os
import json
from .mos import materials, meshes, models, level

"""
bl_info = {
    "name":         "General level format",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 7),
    "version":      (0, 0, 2),
    "location":     "File > Import-Export",
    "description":  "Export general level",
    "category":     "Import-Export"
}
"""




class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.json"
    bl_label = "General level format"
    bl_options = {'PRESET'}
    filename_ext = ".json"

    def execute(self, context):
        level.write(os.path.dirname(self.filepath))


def menu_func(self, context):
    self.layout.operator(ExportMyFormat.bl_idname, text="General level format(.json)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
