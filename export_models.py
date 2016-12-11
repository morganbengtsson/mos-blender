"""bl_info = {
    "name":         "Model format",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 1),
    "version":      (0, 0, 1),
    "location":     "File > Import-Export",
    "description":  "Export Models",
    "category":     "Import-Export"
}"""
        
import bpy
from bpy_extras.io_utils import ExportHelper
import os
import mathutils
import copy
import json
from .mos import materials, meshes, models

"""
def add_popup(blender_object, element):
    object_field = ET.SubElement(element, "popup")
    print(str(blender_object.get("init_time")))
    print(str(blender_object.get("text")))
    object_field.set("init_time", str(blender_object.get("init_time")))
    object_field.set("text", str(blender_object.get("text")))
"""


class ExportModelsFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_models.model"
    bl_label = "Model format"
    bl_options = {'PRESET'}
    filename_ext = ".model"

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects if not o.parent and (o.type == 'MESH' or (o.type == 'EMPTY' and o.children))]

        dir = os.path.dirname(self.filepath)

        print("Writing models.")
        models.write(dir, blender_objects)
        print("Writing materials.")
        materials.write(dir)
        print("Writing meshes.")
        meshes.write(dir, [o for o in bpy.data.objects if o.type == "MESH"])

        return {'FINISHED'}


def export_models_menu_func(self, context):
    self.layout.operator(ExportModelsFormat.bl_idname, text="Model format(.model)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(export_models_menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(export_models_menu_func)

if __name__ == "__main__":
    register()
