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

class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname = "export_sirkel_level.slf"
    bl_label = "Sirkel level format"
    bl_options = {'PRESET'}
    filename_ext = ".slf"

    def execute(self, context):
        path = bpy.path.abspath('//') #root directory
        objects = context.scene.objects
        root = ET.Element("scene")
        for ob in objects:
            object_field = ET.SubElement(root, "object")
            object_field.set("name", ob.name)
            object_field.set("x", str(ob.location[0]))
            object_field.set("y", str(ob.location[1]))
            object_field.set("z", str(ob.location[2]))
            object_field.set("angle", str(ob.rotation_euler[2]))
            object_field.text = ob.name
            bpy.ops.export_scene.obj(filepath = str(path + ob.name + '.obj'), use_normals=True, use_uvs=True, use_triangles=True)
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
