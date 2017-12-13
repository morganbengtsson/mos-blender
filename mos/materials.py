import bpy
import struct
import json


def get_linked_map(input_name, node):
    node_input = node.inputs.get("Color")
    linked_map = None
    if node_input.is_linked:
        linked_map = node_input.links[0].from_node.image.name
    return linked_map


def write(dir):
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        material_file = open(dir + '/' + blender_material.name + '.material', 'bw')

        print('Exporting: ' + blender_material.name)
        node = blender_material.node_tree.nodes.get("Material Output").inputs[0].links[0].from_node

        albedo = (0.0, 0.0, 0.0) if color_input.default_value[:3] is None else color_input.default_value[:3]

        albedo_map = None
        color_input = node.inputs.get("Color")
        if color_input.is_linked:
            albedo_map = color_input.links[0].from_node.image.name

        normal_map = None
        normal_input = node.inputs.get("Normal")
        if normal_input.is_linked:
            normal_map = normal_input.links[0].from_node.image.name

        metallic_map = None
        metallic_input = node.inputs.get("Metallic")
        if metallic_input.is_linked:
            metallic_map = metallic_input.links[0].from_node.image.name

        roughness = node.inputs.get("Roughness").default_value
        metallic = node.inputs.get("Metallic").default_value

        material = {"albedo": tuple(albedo),
                    "opacity": blender_material.alpha,
                    "roughness": float(roughness),
                    "metallic": float(metallic),
                    "albedo_map": albedo_map,
                    "normal_map": normal_map,
                    "metallic_map": metallic_map,
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





