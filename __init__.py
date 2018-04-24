import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
import os
from .mos import level, materials, meshes, entities

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


class ExportMaterialsFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.material"
    bl_label = "Export MOS materials"
    bl_options = {'PRESET'}
    filename_ext = ".material"

    def execute(self, context):
        materials.write(os.path.dirname(self.filepath))
        return {'FINISHED'}


class ExportMeshesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.mesh"
    bl_label = "Export MOS meshes"
    bl_options = {'PRESET'}
    filename_ext = ".mesh"

    def execute(self, context):
        meshes.write(os.path.dirname(self.filepath), context.selected_objects)
        return {'FINISHED'}


class ExportEntitiesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_entities.model"
    bl_label = "Export MOS entities/models"
    bl_options = {'PRESET'}
    filename_ext = ".model .{entity_type}"

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects]
        dir = os.path.dirname(self.filepath)
        entities.write(dir, blender_objects)

        return {'FINISHED'}


def export_level_menu_func(self, context):
    self.layout.operator(ExportLevelFormat.bl_idname, text=ExportLevelFormat.bl_label[7:] + " (%s)" % ExportLevelFormat.filename_ext)


def export_materials_menu_func(self, context):
    self.layout.operator(ExportMaterialsFormat.bl_idname, text=ExportMaterialsFormat.bl_label[7:] + " (%s)" % ExportMaterialsFormat.filename_ext)


def export_meshes_menu_func(self, context):
    self.layout.operator(ExportMeshesFormat.bl_idname, text=ExportMeshesFormat.bl_label[7:] + " (%s)" % ExportMeshesFormat.filename_ext)


def export_entities_menu_func(self, context):
    self.layout.operator(ExportEntitiesFormat.bl_idname, text=ExportEntitiesFormat.bl_label[7:] + " (%s)" % ExportEntitiesFormat.filename_ext)

def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(export_level_menu_func)
    bpy.types.INFO_MT_file_export.append(export_materials_menu_func)
    bpy.types.INFO_MT_file_export.append(export_meshes_menu_func)
    bpy.types.INFO_MT_file_export.append(export_entities_menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(export_level_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_materials_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_meshes_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_entities_menu_func)



if __name__ == "__main__":
    register()

