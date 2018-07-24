import bpy
import struct
import json
import os


def get_linked_map(input_name, node):
    node_input = node.inputs.get(input_name)
    linked_map = None
    if node_input.is_linked:
        linked_map = node_input.links[0].from_node.image.name
    return linked_map


def material_path(blender_material: bpy.types.Material):
    library = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0] + '/'
    if blender_material.library:
        library, file_extension = os.path.splitext(blender_material.library.filepath)
        library = library + '/'
    path = library + blender_material.name + ".material"
    return path.strip('/')


def write(directory):
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        node = blender_material.node_tree.nodes.get("Material Output").inputs[0].links[0].from_node

        color_input = node.inputs.get("Color")
        albedo_map = get_linked_map("Color", node)
        albedo = (0.0, 0.0, 0.0) if not color_input.default_value[:3] else color_input.default_value[:3]

        emission_input = node.inputs.get("Emission")
        emission_map = get_linked_map("Emission", node)
        emission = (0.0, 0.0, 0.0) if not emission_input.default_value[:3] else emission_input.default_value[:3]

        normal_map = get_linked_map("Normal", node)
        metallic_map = get_linked_map("Metallic", node)
        roughness_map = get_linked_map("Roughness", node)
        ambient_occlusion_map = get_linked_map("Ambient occlusion", node)

        roughness = node.inputs.get("Roughness").default_value
        metallic = node.inputs.get("Metallic").default_value
        opacity = node.inputs.get("Opacity").default_value
        ambient_occlusion = node.inputs.get("Ambient occlusion").default_value

        material = {"albedo": tuple(albedo),
                    "opacity": opacity,
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

        library = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0] + '/'
        if blender_material.library:
            library, file_extension = os.path.splitext(blender_material.library.filepath)
            library = library + '/'

        filepath = directory + '/' + material_path(blender_material)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        print('Wrote: ' + filepath)

        json_file = open(filepath, 'w')
        json.dump(material, json_file)
        json_file.close()

