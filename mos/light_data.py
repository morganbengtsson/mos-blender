import bpy
import json
from .common import *


def light_data_path(blender_object):
    path = library_path(blender_object) + "light_data/" + blender_object.name + ".light_data"
    return path.strip('/')


def write(report, directory):
    blender_lamps = bpy.data.lights

    for blender_lamp in blender_lamps:
        if blender_lamp.use_nodes:
            node = blender_lamp.node_tree.nodes.get("Emission")
            color_input = node.inputs.get("Color")
            color = color_input.default_value[:3]

            strength_input = node.inputs.get("Strength")
            strength = strength_input.default_value
        else:
            color = blender_lamp.color[:3]
            strength = blender_lamp.energy

        spot_size = blender_lamp.spot_size
        spot_blend = blender_lamp.spot_blend
        near = blender_lamp.shadow_buffer_clip_start
        far = blender_lamp.cutoff_distance

        light = {"color": tuple(color),
                 "strength": float(strength),
                 "size": float(spot_size),
                 "blend": float(spot_blend),
                 "near": float(near),
                 "far": float(far)}

        path = directory + '/' + light_data_path(blender_lamp)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json_file = open(path, 'w')
        json.dump(light, json_file)
        json_file.close()
        report({'INFO'}, 'Wrote: ' + path)
    report({'INFO'}, "Wrote all light data.")
