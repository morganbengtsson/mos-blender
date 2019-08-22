import bpy
import json
from shutil import copyfile
from .common import *


def copy_linked_map(input_name, directory, blender_material, node):
    if not node:
        return None
    node_input = node.inputs.get(input_name)
    if not node_input:
        return None
    image_path = None
    texture_path = None
    if node_input.is_linked:
        texture_node = node_input.links[0].from_node
        image = texture_node.image
        filename = image.name
        source_filepath = bpy.path.abspath(image.filepath, library=image.library)
        image_path = library_path(blender_material) + "images/" + filename
        full_image_path = directory + '/' + image_path
        os.makedirs(os.path.dirname(full_image_path), exist_ok=True)
        copyfile(source_filepath, full_image_path)

        interpolation = texture_node.interpolation.lower()
        if interpolation not in {"linear", "closest"}:
            raise Exception("Interpolation not supported")

        texture = {"filtering": interpolation,
                   "image": image_path}

        texture_path = library_path(blender_material) + "textures/" + image.name + ".texture"
        texture_path = texture_path.strip('/')

        path = directory + '/' + texture_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json_file = open(path, 'w')
        json.dump(texture, json_file)
        json_file.close()

    return texture_path


def material_path(blender_material: bpy.types.Material):
    path = library_path(blender_material) + "materials/" + blender_material.name + ".material"
    return path.strip('/')


def write(report, directory):
    blender_materials = bpy.data.materials

    for blender_material in blender_materials:
        print("WRITING " + str(blender_material.name))
        report({'INFO'}, "Writing: " + str(blender_material.name))
        try:
            node = next(n for n in blender_material.node_tree.nodes.values() if n.bl_idname == "ShaderNodeOutputMaterial").inputs[0].links[0].from_node

            if node.bl_idname != "ShaderNodeBsdfPrincipled":
                raise Exception("Material node must be Principled.")

            albedo_input = node.inputs.get("Base Color")
            albedo_map = copy_linked_map("Base Color", directory, blender_material, node)
            albedo = (0.0, 0.0, 0.0) if not albedo_input.default_value[:3] else albedo_input.default_value[:3]

            normal_input = node.inputs.get("Normal")
            normal_map_node = normal_input.links[0].from_node if normal_input.is_linked else None
            normal_map = copy_linked_map("Color", directory, blender_material, normal_map_node) if normal_map_node else None

            metallic_map = copy_linked_map("Metallic", directory, blender_material, node)
            roughness_map = copy_linked_map("Roughness", directory, blender_material, node)
            emission_map = copy_linked_map("Emission", directory, blender_material, node)

            roughness = node.inputs.get("Roughness").default_value
            metallic = node.inputs.get("Metallic").default_value
            alpha = node.inputs.get("Alpha").default_value
            index_of_refraction = node.inputs.get("IOR").default_value
            emission = node.inputs.get("Emission").default_value
            transmission = node.inputs.get("Transmission").default_value

            mos_node = next((n for n in blender_material.node_tree.nodes.values() if n.name == "MOS"), None)
            ambient_occlusion_input = mos_node.inputs.get("Ambient Occlusion") if mos_node else None
            ambient_occlusion = ambient_occlusion_input.default_value if ambient_occlusion_input else 1.0

            ambient_occlusion_map = copy_linked_map("Ambient Occlusion", directory, blender_material, mos_node)

            material = {"albedo": tuple(albedo),
                        "alpha": float(alpha),
                        "index_of_refraction": index_of_refraction,
                        "transmission": transmission,
                        "roughness": float(roughness),
                        "metallic": float(metallic),
                        "emission": tuple(emission),
                        "ambient_occlusion": float(ambient_occlusion),
                        "albedo_map": albedo_map,
                        "normal_map": normal_map,
                        "metallic_map": metallic_map,
                        "roughness_map": roughness_map,
                        "emission_map": emission_map,
                        "ambient_occlusion_map": ambient_occlusion_map}

            path = directory + '/' + material_path(blender_material)
            os.makedirs(os.path.dirname(path), exist_ok=True)

            json_file = open(path, 'w')
            json.dump(material, json_file)
            json_file.close()

        except Exception as e:
            raise Exception('Error writing material ' + blender_material.name) from e

        report({'INFO'}, "Wrote: " + path)
        report({'INFO'}, "Wrote material " + blender_material.name)
    report({'INFO'}, "Wrote all materials.")
