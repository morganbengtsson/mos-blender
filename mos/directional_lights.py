import bpy
import json
from .common import *


def directional_light_path(blender_object):
    path = library_path(blender_object) + "directional_lights/" + blender_object.name + ".directional_light"
    return path.strip('/')


def write(report, directory):
    blender_directional_lights = [l for l in bpy.data.lights if l.type == "SUN"]

    for blender_lamp in blender_directional_lights:
        if blender_lamp.use_nodes:
            node = blender_lamp.node_tree.nodes.get("Emission")
            color_input = node.inputs.get("Color")
            color = color_input.default_value[:3]

            strength_input = node.inputs.get("Strength")
            strength = strength_input.default_value
        else:
            color = blender_lamp.color[:3]
            strength = blender_lamp.energy
        
        #TODO: Add number of cascades

        directional_light = {"color": tuple(color),
                 "strength": float(strength)}

        path = directory + '/' + directional_light_path(blender_lamp)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json_file = open(path, 'w')
        json.dump(directional_light, json_file)
        json_file.close()
        report({'INFO'}, 'Wrote: ' + path)
    report({'INFO'}, "Wrote all directional lights.")
