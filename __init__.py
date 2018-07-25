import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
import bmesh
import os
from .mos import level, materials, meshes, entities, light_data

bl_info = {
    "name":         "Mos export",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 7),
    "version":      (0, 0, 3),
    "location":     "File > Import-Export",
    "description":  "Export Mos formats",
    "category":     "Import-Export"
}


class ExportLevelFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.level"
    bl_label = "Export MOS level"
    bl_options = {'PRESET'}
    filename_ext = ".level"

    def execute(self, context):
        level.write(os.path.dirname(self.filepath), self.filepath, context.scene.objects)
        return {'FINISHED'}


class ExportEntitiesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_entities.entity"
    bl_label = "Export MOS entities"
    bl_options = {'PRESET'}
    filename_ext = "."
    use_filter_folder = True

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects]
        directory = os.path.dirname(self.filepath)
        entities.write(directory, blender_objects)

        return {'FINISHED'}


def export_level_menu_func(self, context):
    self.layout.operator(ExportLevelFormat.bl_idname, text=ExportLevelFormat.bl_label[7:] + " (%s)" % ExportLevelFormat.filename_ext)


def export_entities_menu_func(self, context):
    self.layout.operator(ExportEntitiesFormat.bl_idname, text=ExportEntitiesFormat.bl_label[7:] + " (%s)" % ExportEntitiesFormat.filename_ext)


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(export_level_menu_func)
    bpy.types.INFO_MT_file_export.append(export_entities_menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(export_level_menu_func)

    bpy.types.INFO_MT_file_export.remove(export_entities_menu_func)


if __name__ == "__main__":
    register()

