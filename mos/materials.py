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

        texture_filter = texture_node.interpolation.lower()
        if texture_filter not in {"linear", "closest"}:
            raise Exception("Interpolation not supported")

        texture_wrap = "repeat" if texture_node.extension.lower() == "repeat" else "clamp"

        texture = {"filter": texture_filter,
                   "wrap": texture_wrap,
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
        print(blender_material.name)
        print(blender_material.use_nodes)
        print(blender_material.node_tree)
        if blender_material.use_nodes and blender_material.node_tree:
            print("WRITING " + str(blender_material.name))
            report({'INFO'}, "Writing: " + str(blender_material.name))
            try:
                node = next(n for n in blender_material.node_tree.nodes.values() if n.bl_idname == "ShaderNodeOutputMaterial").inputs[0].links[0].from_node

                if node.bl_idname != "ShaderNodeBsdfPrincipled":
                    raise Exception("Material node must be Principled.")

                albedo_input = node.inputs.get("Base Color")

                albedo_map = copy_linked_map("Base Color", directory, blender_material, node)
                albedo_value = (0.0, 0.0, 0.0) if not albedo_input.default_value[:3] else albedo_input.default_value[:3]

                normal_input = node.inputs.get("Normal")
                normal_map_node = normal_input.links[0].from_node if normal_input.is_linked else None
                normal_map = copy_linked_map("Color", directory, blender_material, normal_map_node) if normal_map_node else None

                metallic_map = copy_linked_map("Metallic", directory, blender_material, node)
                metallic_value = node.inputs.get("Metallic").default_value

                roughness_map = copy_linked_map("Roughness", directory, blender_material, node)
                roughness_value = node.inputs.get("Roughness").default_value

                emission_map = copy_linked_map("Emission", directory, blender_material, node)
                emission_value = node.inputs.get("Emission").default_value

                mos_node = next((n for n in blender_material.node_tree.nodes.values() if n.name == "MOS"), None)
                ambient_occlusion_input = mos_node.inputs.get("Ambient Occlusion") if mos_node else None
                ambient_occlusion_value = ambient_occlusion_input.default_value if ambient_occlusion_input else 1.0
                ambient_occlusion_map = copy_linked_map("Ambient Occlusion", directory, blender_material, mos_node)

                alpha = node.inputs.get("Alpha").default_value
                index_of_refraction = node.inputs.get("IOR").default_value
                transmission = node.inputs.get("Transmission").default_value


                material = {"albedo": {"value": tuple(albedo_value), "texture": albedo_map},
                            "roughness": {"value": float(roughness_value), "texture": roughness_map},
                            "metallic": {"value": float(metallic_value), "texture": metallic_map},
                            "emission": {"value": tuple(emission_value), "texture": emission_map},
                            "ambient_occlusion": {"value": float(ambient_occlusion_value),
                                                "texture": ambient_occlusion_map},
                            "normal": {"texture": normal_map},
                            "alpha": float(alpha),
                            "index_of_refraction": index_of_refraction,
                            "transmission": transmission,
                            }

                path = directory + '/' + material_path(blender_material)
                os.makedirs(os.path.dirname(path), exist_ok=True)


                json_file = open(path, 'w')
                json.dump(material, json_file)
                json_file.close()

            except Exception as e:
                raise Exception('Error writing material ' + blender_material.name) from e

            report({'INFO'}, "Wrote: " + path)
            report({'INFO'}, "Wrote material " + blender_material.name)
        else:
            report({'WARNING'}, "Did not write material {}".format(blender_material.name))
    report({'INFO'}, "Wrote all materials.")
