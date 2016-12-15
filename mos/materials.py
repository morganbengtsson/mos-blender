import bpy
import struct
import json


def write(dir):
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        material_file = open(dir + '/' + blender_material.name + '.material', 'bw')

        print('Exporting: ' + blender_material.name)

        material = {"ambient": tuple(blender_material.diffuse_color * blender_material.ambient),
                    "diffuse": tuple(blender_material.diffuse_color),
                    "specular": tuple(blender_material.specular_color),
                    "opacity": blender_material.alpha,
                    "specular_exponent": float(blender_material.specular_hardness),
                    "texture": blender_material.get("texture"),
                    "normalmap" : blender_material.get("normalmap")}

        print(material)

        material_file.write(struct.pack('fff', *material["ambient"]))
        material_file.write(struct.pack('fff', *material["diffuse"]))
        material_file.write(struct.pack('fff', *material["specular"]))

        material_file.write(struct.pack('f', material["opacity"]))
        material_file.write(struct.pack('f', material["specular_exponent"]))

        material_file.close()
        print("Wrote file: " + material_file.name)

        json_file = open(dir + '/' + blender_material.name + '.material', 'w')
        json.dump(material, json_file)
        json_file.close()

