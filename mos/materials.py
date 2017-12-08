import bpy
import struct
import json


def write(dir):
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        material_file = open(dir + '/' + blender_material.name + '.material', 'bw')

        print('Exporting: ' + blender_material.name)

        # albedo = blender_material.node_tree.nodes["Glossy BSDF"].inputs[0].default_value
        # roughness = blender_material.node_tree.nodes["Glossy BSDF"].inputs[1].default_value

        albedo = blender_material.node_tree.nodes.get("Glossy BSDF").inputs[0].default_value[:3]
        roughness = blender_material.node_tree.nodes.get("Glossy BSDF").inputs[1].default_value

        material = {"albedo": tuple(albedo),
                    "opacity": blender_material.alpha,
                    "roughness": float(roughness),
                    "albedo_map": blender_material.get("albedo_map"),
                    "normal_map": blender_material.get("normal_map"),
                    "light_map": blender_material.get("light_map")}

        print(material)
        material_file.write(struct.pack('fff', *material["albedo"]))
        material_file.write(struct.pack('f', material["opacity"]))
        material_file.write(struct.pack('f', material["roughness"]))

        material_file.close()
        print("Wrote file: " + material_file.name)

        json_file = open(dir + '/' + blender_material.name + '.material', 'w')
        json.dump(material, json_file)
        json_file.close()

