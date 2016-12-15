import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
import os
from .mos import level, materials, meshes, models, entities

bl_info = {
    "name":         "Mos export",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 7),
    "version":      (0, 0, 2),
    "location":     "File > Import-Export",
    "description":  "Export Mos formats",
    "category":     "Import-Export"
}


class ExportLevelFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.json"
    bl_label = "MOS general level format (.json)"
    bl_options = {'PRESET'}
    filename_ext = ".json"

    def execute(self, context):
        level.write(os.path.dirname(self.filepath), self.filepath, context.scene.objects)
        return {'FINISHED'}


class ExportMaterialsFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.material"
    bl_label = "MOS material format (.material)"
    bl_options = {'PRESET'}
    filename_ext = ".material"

    def execute(self, context):
        materials.write(os.path.dirname(self.filepath))
        return {'FINISHED'}


class ExportMeshesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_mesh.mesh"
    bl_label = "MOS mesh format (.mesh)"
    bl_options = {'PRESET'}
    filename_ext = ".mesh"

    def execute(self, context):
        meshes.write(os.path.dirname(self.filepath), context.selected_objects)
        return {'FINISHED'}


class ExportEntitiesFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_entities.entity"
    bl_label = "MOS entity format (.entity)"
    bl_options = {'PRESET'}
    filename_ext = ".entity"

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects if not o.parent and o.type in {"MESH", "EMPTY"}]
        directory = os.path.dirname(self.filepath)
        entities.write(directory, blender_objects)
        return {'FINISHED'}


class ExportModelsFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_models.model"
    bl_label = "MOS model format (.model)"
    bl_options = {'PRESET'}
    filename_ext = ".model"

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects if not o.parent and (o.type == 'MESH' or (o.type == 'EMPTY' and o.children))]
        dir = os.path.dirname(self.filepath)
        models.write(dir, blender_objects)

        return {'FINISHED'}


def export_level_menu_func(self, context):
    self.layout.operator(ExportLevelFormat.bl_idname, text=ExportLevelFormat.bl_label)


def export_materials_menu_func(self, context):
    self.layout.operator(ExportMaterialsFormat.bl_idname, text=ExportMaterialsFormat.bl_label)


def export_meshes_menu_func(self, context):
    self.layout.operator(ExportMeshesFormat.bl_idname, text=ExportMeshesFormat.bl_label)


def export_models_menu_func(self, context):
    self.layout.operator(ExportModelsFormat.bl_idname, text=ExportModelsFormat.bl_label)


def export_entities_level_func(self, context):
    self.layout.operator(ExportEntitiesFormat.bl_idname, text=ExportEntitiesFormat.bl_label)






def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(export_level_menu_func)
    bpy.types.INFO_MT_file_export.append(export_materials_menu_func)
    bpy.types.INFO_MT_file_export.append(export_meshes_menu_func)
    bpy.types.INFO_MT_file_export.append(export_models_menu_func)
    bpy.types.INFO_MT_file_export.append(export_entities_level_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(export_level_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_materials_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_meshes_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_models_menu_func)
    bpy.types.INFO_MT_file_export.remove(export_entities_level_func)


if __name__ == "__main__":
    register()
