import bpy
import struct
import json


def get_linked_map(input_name, node):
    node_input = node.inputs.get(input_name)
    linked_map = None
    if node_input.is_linked:
        linked_map = node_input.links[0].from_node.image.name
    return linked_map


def write(dir):
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        print('Exporting: ' + blender_material.name)
        node = blender_material.node_tree.nodes.get("Material Output").inputs[0].links[0].from_node

        color_input = node.inputs.get("Color")
        albedo = (0.0, 0.0, 0.0) if color_input.default_value[:3] is None else color_input.default_value[:3]
        albedo_map = get_linked_map("Color", node)

        emission_input = node.inputs.get("Emission")
        emission = (0.0, 0.0, 0.0) if emission_input.default_value[:3] is None else emission_input.default_value[:3]
        emission_map = get_linked_map("Emission", node)

        normal_map = get_linked_map("Normal", node)
        metallic_map = get_linked_map("Metallic", node)
        roughness_map = get_linked_map("Roughness", node)
        ambient_occlusion_map = get_linked_map("Ambient occlusion", node)

        roughness = node.inputs.get("Roughness").default_value
        metallic = node.inputs.get("Metallic").default_value
        ambient_occlusion = node.inputs.get("Ambient occlusion").default_value

        material = {"albedo": tuple(albedo),
                    "opacity": blender_material.alpha,
                    "roughness": float(roughness),
                    "metallic": float(metallic),
                    "emission": tuple(emission),
                    "ambient_occlusion": float(ambient_occlusion),
                    "albedo_map": albedo_map,
                    "emission_map": emission_map,
                    "normal_map": normal_map,
                    "metallic_map": metallic_map,
                    "roughness_map": roughness_map,
                    "ambient_occlusion_map": ambient_occlusion_map}

        json_file = open(dir + '/' + blender_material.name + '.material', 'w')
        json.dump(material, json_file)
        json_file.close()
        print("Wrote file: " + blender_material.name + ".material")





