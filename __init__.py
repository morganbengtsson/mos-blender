bl_info = {
    "name":         "Room level format",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 7, 1),
    "version":      (0, 0, 1),
    "location":     "File > Import-Export",
    "description":  "Export Room level",
    "category":     "Import-Export"
}
        
import bpy
from bpy_extras.io_utils import ExportHelper
import os
import mathutils
import copy
import json
from mo import materials, meshes


def to_level_object(blender_object):
    if not blender_object:
        return None

    level_object = dict()
    level_object['type'] = blender_object.get('type') or 'mesh'
    level_object['name'] = blender_object.name

    location = blender_object.location
    print (blender_object.rotation_mode)
    blender_object.rotation_mode ='AXIS_ANGLE'
    axis_angle = blender_object.rotation_axis_angle
    level_object['axis'] = [axis_angle[1], axis_angle[2], axis_angle[3]]
    level_object['angle'] = axis_angle[0]
    level_object['euler'] = [blender_object.rotation_euler[0], blender_object.rotation_euler[1], blender_object.rotation_euler[2]]
    blender_object.rotation_mode = 'XYZ'

    level_object['position'] = [location[0], location[1], location[2]]
    if blender_object.type == "MESH":
        level_object['mesh'] = str(blender_object.name + '.mesh')

    if blender_object.active_material:
        level_object['material'] = str(blender_object.active_material.name + '.material')
    #else :
        #level_object['material'] = 'wall.material'

    if blender_object.get("selectable") is not None:
        level_object["selectable"] = bool(blender_object.get("selectable"))

    if blender_object.get("texture") is not None:
        level_object['texture'] = blender_object.get('texture')

    if blender_object.get("lightmap") is not None:
        level_object['lightmap'] = blender_object.get('lightmap')

    if level_object["type"] in {"soundsource", "streamsource", "train", "person"}:
        level_object["stream"] = blender_object.get("stream")
        level_object["sound"] = blender_object.get("sound")
        level_object["file"] = blender_object.get("file")
        level_object["gain"] = float(blender_object.get("gain") or 1.0)
        level_object["pitch"] = float(blender_object.get("pitch") or 1.0)


    return level_object

def to_level_objects(blender_objects):
    root = []
    for object in blender_objects:
            level_object = to_level_object(object)
            level_object['children'] = to_level_objects(object.children)
            root.append(level_object)
    return root

def add_popup(blender_object, element):
    object_field = ET.SubElement(element, "popup")
    print(str(blender_object.get("init_time")))
    print(str(blender_object.get("text")))
    object_field.set("init_time", str(blender_object.get("init_time")))
    object_field.set("text", str(blender_object.get("text")))


class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_rom_level.json"
    bl_label = "Room level format"
    bl_options = {'PRESET'}
    filename_ext = ".json"

    def execute(self, context):
        blender_objects = [o for o in bpy.data.objects if (o.type == 'MESH' or (o.type == 'EMPTY' and o.children)) or o.get("type") == "streamsource" and not o.parent]

        root = to_level_objects(blender_objects)

        file = open(self.filepath, 'w')
        file.write(json.dumps(root))
        file.close()

        dir = os.path.dirname(self.filepath)

        print("Writing materials")
        materials.write(dir)
        print("Writing meshes")
        meshes.write(dir)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ExportMyFormat.bl_idname, text="Room level format(.json)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
