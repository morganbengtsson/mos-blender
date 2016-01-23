import bpy
from bpy_extras.io_utils import ExportHelper
import os
import json
from mo import materials, meshes, models

bl_info = {
    "name":         "General level format",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 1),
    "version":      (0, 0, 1),
    "location":     "File > Import-Export",
    "description":  "Export general level",
    "category":     "Import-Export"
}


def to_entity(directory, blender_object):
    entity_type = blender_object.get("entity_type")
    print("type: ", end=" ")
    print(entity_type)

    if not blender_object or blender_object.type not in {"MESH", "EMPTY"}:
        return None

    entity = dict()

    keys = blender_object.keys()
    for key in keys:
        if not key.startswith("_") and not key.startswith("cycles"):
            entity[key] = blender_object[key]

    entity['type'] = entity_type
    entity['name'] = blender_object.name

    m = blender_object.matrix_local
    location = [m[0][3], m[1][3], m[2][3]]

    entity['position'] = [location[0], location[1], location[2]]

    transform = list()
    for row in m.col:
        transform.extend(list(row))
    entity["transform"] = transform

    print("Writing models.")
    print(True if entity_type is None else False)
    models.write(directory, [blender_object], True if entity_type is None else False)

    entity["model"] = blender_object.name + ".model"
    entity["id"] = blender_object.as_pointer()

    return entity


def to_entities(directory, blender_objects):
    root = []
    for blender_object in blender_objects:
        level_object = to_entity(directory, blender_object)
        if level_object:
            level_object['children'] = to_entities(directory, blender_object.children)
            root.append(level_object)
    return root


class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_rom_level.json"
    bl_label = "General level format"
    bl_options = {'PRESET'}
    filename_ext = ".json"

    def execute(self, context):
        blender_objects = [o for o in context.scene.objects if not o.parent and o.type in {"MESH", "EMPTY"}]

        directory = os.path.dirname(self.filepath)

        root = to_entities(directory, blender_objects)

        print("Writing entities.")
        file = open(self.filepath, 'w')
        file.write(json.dumps(root))
        file.close()

        objects = context.scene.objects

        print("Writing materials.")
        materials.write(directory)
        print("Writing meshes.")
        meshes.write(directory, [o for o in objects if o.type == "MESH"])

        return {'FINISHED'}


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
