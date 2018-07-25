import bpy
import struct
import json
import os
from shutil import copyfile


def copy_linked_map(input_name, directory, blender_material, node):
    node_input = node.inputs.get(input_name)
    path = None
    if node_input.is_linked:
        image = node_input.links[0].from_node.image
        linked_map = image.name
        source_path = bpy.path.abspath(image.filepath, library=image.library)

        library = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0] + '/'
        if blender_material.library:
            library, file_extension = os.path.splitext(blender_material.library.filepath)
            library = library + '/'
        path = library + "textures/" + linked_map
        full_path = directory + '/' + path
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        copyfile(source_path, full_path)
    return path


def material_path(blender_material: bpy.types.Material):
    library = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0] + '/'
    if blender_material.library:
        library, file_extension = os.path.splitext(blender_material.library.filepath)
        library = library + '/'
    path = library + blender_material.name + ".material"
    return path.strip('/')


def write(directory):
    print("Writing materials.")
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        node = blender_material.node_tree.nodes.get("Material Output").inputs[0].links[0].from_node

        color_input = node.inputs.get("Color")
        albedo_map = copy_linked_map("Color", directory, blender_material, node)
        albedo = (0.0, 0.0, 0.0) if not color_input.default_value[:3] else color_input.default_value[:3]

        emission_input = node.inputs.get("Emission")
        emission_map = copy_linked_map("Emission",directory, blender_material, node)
        emission = (0.0, 0.0, 0.0) if not emission_input.default_value[:3] else emission_input.default_value[:3]

        normal_map = copy_linked_map("Normal", directory, blender_material, node)
        metallic_map = copy_linked_map("Metallic", directory, blender_material, node)
        roughness_map = copy_linked_map("Roughness", directory, blender_material, node)
        ambient_occlusion_map = copy_linked_map("Ambient occlusion", directory, blender_material, node)

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

        filepath = directory + '/' + material_path(blender_material)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        json_file = open(filepath, 'w')
        json.dump(material, json_file)
        json_file.close()

        print('Wrote: ' + filepath)

