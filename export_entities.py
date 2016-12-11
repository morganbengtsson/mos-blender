import bpy
from bpy_extras.io_utils import ExportHelper
import os
import json
from .mos import materials, meshes, models, entities

"""
bl_info = {
    "name":         "Entities",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 7),
    "version":      (0, 0, 3),
    "location":     "File > Import-Export",
    "description":  "Export entities",
    "category":     "Import-Export"
}
"""


class ExportEntitiesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_entities.entity"
    bl_label = "Entities"
    bl_options = {'PRESET'}
    filename_ext = ".entity"

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects if not o.parent and o.type in {"MESH", "EMPTY"}]
        directory = os.path.dirname(self.filepath)
        entities.write(directory, blender_objects)
        return {'FINISHED'}


def export_entities_level_func(self, context):
    self.layout.operator(ExportEntitiesFormat.bl_idname, text="Entity format (.entity)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(export_entities_level_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(export_entities_level_func)

if __name__ == "__main__":
    register()