import bpy
import json
import os


def light_data_path(blender_object):
    path = ""
    if blender_object.library:
        path, file_extension = os.path.splitext(blender_object.library.filepath)
        path = path + '/'
    path += blender_object.name + '.light_data'
    return path.strip('/')


def write(directory):
    blender_lamps = bpy.data.lamps

    for blender_lamp in blender_lamps:
        node = blender_lamp.node_tree.nodes.get("Emission")
        color_input = node.inputs.get("Color")
        color = color_input.default_value[:3]

        strength_input = node.inputs.get("Strength")
        strength = strength_input.default_value

        spot_size = blender_lamp.spot_size
        spot_blend = blender_lamp.spot_blend

        light = {"color": tuple(color),
                 "strength": float(strength),
                 "size": float(spot_size),
                 "blend": float(spot_blend)}

        filepath = directory + light_data_path(blender_lamp)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        print('Exporting: ' + filepath)
        json_file = open(filepath, 'w')
        json.dump(light, json_file)
        json_file.close()
