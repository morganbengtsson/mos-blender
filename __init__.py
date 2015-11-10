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
from mo import materials, meshes, models


def to_level_object(blender_object):
    if not blender_object:
        return None

    level_object = dict()
    level_object['type'] = blender_object.get('type') or 'mesh'
    level_object['name'] = blender_object.name



    m = blender_object.matrix_local
    location = [m[0][3], m[1][3], m[2][3]]

    #if blender_object.parent:
        #print (blender_object.parent.location + blender_object.location)
        #m = blender_object.parent.matrix_world * blender_object.matrix_parent_inverse * blender_object.matrix_local
    #    m = blender_object.parent.matrix_world * blender_object.matrix_local
    #    location = [m[0][3], m[1][3], m[2][3]]

    blender_object.rotation_mode ='AXIS_ANGLE'
    axis_angle = blender_object.rotation_axis_angle
    level_object['axis'] = [axis_angle[1], axis_angle[2], axis_angle[3]]
    level_object['angle'] = axis_angle[0]
    euler = blender_object.rotation_euler
    level_object['euler'] = [euler[0], euler[1], euler[2]]
    blender_object.rotation_mode = 'XYZ'

    level_object['position'] = [location[0], location[1], location[2]]
    level_object['obstruction'] = blender_object.get('obstruction') or 0.0

    if blender_object.type == "MESH":
        level_object['mesh'] = str(blender_object.name + '.mesh')
        level_object["model"] = blender_object.name + ".model"

    if blender_object.active_material:
        level_object['material'] = str(blender_object.active_material.name + '.material')
    #else :
        #level_object['material'] = 'wall.material'

    if blender_object.get("step") is not None:
        level_object["step"] = bool(blender_object.get("step"))

    if blender_object.get("selectable") is not None:
        level_object["selectable"] = bool(blender_object.get("selectable"))

    if blender_object.get("texture") is not None:
        level_object['texture'] = blender_object.get('texture')

    if blender_object.get("lightmap") is not None:
        level_object['lightmap'] = blender_object.get('lightmap')

    if blender_object.get("texture2") is not None:
        level_object["texture2"] = blender_object.get("texture2")

    if level_object["type"] in {"radio"}:
        level_object["channel1"] = blender_object.get('channel1')
        level_object["channel2"] = blender_object.get('channel2')
        level_object["channel3"] = blender_object.get('channel3')

    if level_object["type"] in {"soundsource", "streamsource", "train", "person", "doorkeypad", "keypad"}:
        level_object["stream"] = blender_object.get("stream")
        level_object["sound"] = blender_object.get("sound")
        level_object["file"] = blender_object.get("file")
        level_object["gain"] = float(blender_object.get("gain") or 1.0)
        level_object["pitch"] = float(blender_object.get("pitch") or 1.0)

    level_object["id"] = blender_object.as_pointer()

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
        blender_objects = [o for o in context.scene.objects if not o.parent and ((o.type == 'MESH' or (o.type == 'EMPTY' and o.children)) or o.get("type") == "streamsource")]

        root = to_level_objects(blender_objects)

        file = open(self.filepath, 'w')
        file.write(json.dumps(root))
        file.close()

        dir = os.path.dirname(self.filepath)

        objects = context.scene.objects

        print("Writing models")
        models.write(dir, [o for o in objects if o.type == "MESH"])
        print("Writing materials")
        materials.write(dir)
        print("Writing meshes")
        meshes.write(dir, [o for o in objects if o.type == "MESH"])

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
