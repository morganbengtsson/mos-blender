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
import xml.etree.cElementTree as ET
import xml.dom.minidom as MD
import os
import mathutils
import copy
from mo import materials, meshes


def add_to_element(blender_object, element, dir):

    object_field = ET.SubElement(element, blender_object.get('type') or 'mesh') #todo change to object
    object_field.set("name", blender_object.name)

    location = blender_object.location

    object_field.set("x", str(location[0]))
    object_field.set("y", str(location[1]))
    object_field.set("z", str(location[2]))
    object_field.set("angle", str(blender_object.rotation_euler[2]))
    object_field.set("mesh", str(blender_object.get("mesh")))
    if blender_object.active_material:
        object_field.set("material", str(blender_object.active_material.name + ".material"))
    if blender_object.get("level"):
        object_field.set("level", str(blender_object.get("level")))

    if "texture" in blender_object:
        object_field.set("texture", blender_object.get("texture"))
    if "lightmap" in blender_object:
        object_field.set("lightmap", blender_object.get("lightmap"))
    if blender_object.active_material:
        diffuse_color = blender_object.active_material.diffuse_color
        object_field.set("r", str(diffuse_color[0]))
        object_field.set("g", str(diffuse_color[1]))
        object_field.set("b", str(diffuse_color[2]))

    return object_field

def add_popup(blender_object, element):
    object_field = ET.SubElement(element, "popup")
    print(str(blender_object.get("init_time")))
    print(str(blender_object.get("text")))
    object_field.set("init_time", str(blender_object.get("init_time")))
    object_field.set("text", str(blender_object.get("text")))


class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_rom_level.rlf"
    bl_label = "Room level format"
    bl_options = {'PRESET'}
    filename_ext = ".rlf"

    #Todo: Export textures along with obj files.
    def execute(self, context):
        graphics_objects = [o for o in bpy.data.objects if (o.type == 'MESH' or o.type == 'EMPTY') and not o.parent]

        root = ET.Element("level")
        root.set("lightmap", str(context.scene.get("lightmap")))
        dir = os.path.dirname(self.filepath)

        for go in graphics_objects:
            field = add_to_element(go, root, dir)
            for po in go.children:
                field2 = add_to_element(po, field, dir)
                for poo in po.children:
                    add_to_element(poo, field2, dir)

        xml = MD.parseString(ET.tostring(root))

        file = open(self.filepath, "w")
        file.write(xml.toprettyxml())
        file.close()

        print("Writing materials")
        materials.write(dir)
        print("Writing meshes")
        meshes.write(dir)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ExportMyFormat.bl_idname, text="Room level format(.rlf)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
