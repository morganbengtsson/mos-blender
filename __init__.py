bl_info = {
    "name":         "Sirkel level format",
    "author":       "Morgan Bengtsson",
    "blender":      (2, 6, 9),
    "version":      (0, 0, 1),
    "location":     "File > Import-Export",
    "description":  "Export Sirkel level",
    "category":     "Import-Export"
}
        
import bpy
from bpy_extras.io_utils import ExportHelper
import xml.etree.cElementTree as ET
import xml.dom.minidom as MD
import os
import mathutils
import copy


def add_to_element(blender_object, element, dir):

    blender_object.select = True
    object_field = ET.SubElement(element, blender_object.get("type") or "object")
    object_field.set("name", blender_object.name)
    object_field.set("x", str(blender_object.location[0]))
    object_field.set("y", str(blender_object.location[1]))
    object_field.set("z", str(blender_object.location[2]))
    object_field.set("angle", str(blender_object.rotation_euler[2]))
    object_field.set("level", str(blender_object.get("level")))
    me = blender_object.data
    if me.uv_textures.active is not None:
        for tf in me.uv_textures.active.data:
            if tf.image:
                img = tf.image.name
                object_field.set("texture", str(img))

    object_field.text = blender_object.name
    matrix = copy.copy(blender_object.matrix_world)
    blender_object.matrix_world = mathutils.Matrix.Identity(4)
    bpy.ops.export_scene.obj(use_selection=True,filepath=os.path.join(dir, blender_object.name + '.obj'), use_normals=True, use_uvs=True, use_triangles=True, axis_forward='Y', axis_up='Z')
    blender_object.select = False #Reset select
    blender_object.matrix_world = matrix #Reset matrix


def add_popup(blender_object, element):
    object_field = ET.SubElement(element, "popup")
    print(str(blender_object.get("init_time")))
    print(str(blender_object.get("text")))
    object_field.set("init_time", str(blender_object.get("init_time")))
    object_field.set("text", str(blender_object.get("text")))


class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_sirkel_level.slf"
    bl_label = "Sirkel level format"
    bl_options = {'PRESET'}
    filename_ext = ".slf"

    #Todo: Export textures along with obj files.
    def execute(self, context):
        dir = os.path.dirname(self.filepath)

        physics_objects = context.scene.objects.get("Physics").children
        graphics_objects = context.scene.objects.get("Graphics").children
        popups = context.scene.objects.get("Popups").children
        start = context.scene.objects.get("Start")
        stop = context.scene.objects.get("Stop")

        root = ET.Element("scene")
        #root.set("nextLevel", context.scene.nextLevel)
        physics = ET.SubElement(root, "physics")
        graphics = ET.SubElement(root, "graphics")

        for ob in physics_objects:
            ob.select = False
        for ob in physics_objects:
            add_to_element(ob, physics, dir)

        for ob in graphics_objects:
            ob.select = False
        for ob in graphics_objects:
            add_to_element(ob, graphics, dir)

        for ob in popups:
            add_popup(ob, root)

        xml = MD.parseString(ET.tostring(root))

        file = open(self.filepath, "w")
        file.write(xml.toprettyxml())
        file.close()

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(ExportMyFormat.bl_idname, text="Sirkel level format(.slf)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
