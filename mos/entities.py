import json
import bpy
import idprop

from . import materials, meshes, spot_lights, directional_lights, sounds
from .common import *


type_map = {
  "MESH": "model",
  "EMPTY": "model",
  "SPEAKER": "sound",
  "CAMERA": "camera",
  "LIGHT" : "light",
  "LIGHT_PROBE": "environment_light"
}


def get_type(blender_object):
    if (blender_object.type == "LIGHT"):
        if (blender_object.data.type == "SPOT"):
            return "spot_light"
        elif (blender_object.data.type == "SUN"):
            return "directional_light"

    return type_map.get(blender_object.type) or "model"


def write_file(report, entity, directory, filepath):
    path = directory + '/' + filepath
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entity_file = open(path, 'w')
    entity_file.write(json.dumps(entity))
    entity_file.close()
    report({'INFO'}, "Wrote: " + path)


def write_entity(report, blender_object, directory):
    if blender_object.type not in type_map.keys():
        report({'INFO'}, "Object type: %s, not supported" % blender_object.type)
    else:
        entity = dict()
        entity["name"] = None
        entity["transform"] = [1, 0, 0, 0,
                          0, 1, 0, 0,
                          0, 0, 1, 0,
                          0, 0, 0, 1]
        entity["position"] = [0, 0, 0]
        entity["rotation"] = [0, 0, 0, 1] #Quaternion
        entity["mesh"] = None
        entity["material"] = None
        entity["sound"] = None
        entity["children"] = list()
        entity["type"] = "model"
        entity["id"] = None
        entity["light"] = None
        entity["bones"] = []


        armature = blender_object.find_armature()
        if armature:
            for bone in armature.data.bones:
                print(bone.matrix_local)
                entity["bones"].append(mat_to_list(bone.matrix_local))


        keys = blender_object.keys()
        for key in keys:
            if not key.startswith("_") and not key.startswith("cycles") and not type(blender_object[key]) is idprop.types.IDPropertyGroup:
                if type(blender_object[key]) is idprop.types.IDPropertyArray:
                    entity[key] = list(blender_object[key])
                else:
                    entity[key] = blender_object[key]

        entity["name"] = blender_object.name

        transform = mat_to_list(blender_object.matrix_local)

        entity["transform"] = transform

        entity["position"] = list(blender_object.location)
        entity["rotation"] = list(blender_object.rotation_quaternion)

        collection = blender_object.instance_collection
        if collection:
            for group_object in sorted(collection.objects, key=lambda x: x.name):
                if not group_object.parent:
                    entity_child = write_entity(report, group_object, directory)
                    if entity_child:
                        entity["children"].append(entity_path(group_object))

        extension = get_type(blender_object)

        entity["type"] = blender_object.get("entity_type") or extension

        entity["id"] = blender_object.as_pointer()

        if entity["type"] == "environment_light":
            entity["extent"] = blender_object.empty_display_size

        if entity["type"] == "camera":
            scene = bpy.context.scene
            aspect = scene.render.resolution_x / scene.render.resolution_y

            entity["aspect"] = aspect

            projection_matrix = blender_object.calc_matrix_camera(depsgraph=bpy.context.evaluated_depsgraph_get(),
                                                                  scale_x=aspect)

            transform = list()
            for row in projection_matrix.col:
                transform.extend(list(row))
            entity["projection"] = transform
            focus_distance = (blender_object.data.dof.focus_object.location - blender_object.location).length if blender_object.data.dof.focus_object else blender_object.data.dof.focus_distance
            entity["focus_distance"] = focus_distance
            entity["far"] = blender_object.data.clip_end
            entity["near"] = blender_object.data.clip_start

        if blender_object.type == "MESH":
            entity["mesh"] = meshes.mesh_path(blender_object)

        if blender_object.type == "LIGHT":
            if (blender_object.data.type == "SPOT") :
                entity["light"] = spot_lights.spot_light_path(blender_object.data)
            elif (blender_object.data.type == "SUN"):
                entity["light"] = directional_lights.directional_light_path(blender_object.data)


        if blender_object.type == "SPEAKER":
            entity["sound"] = sounds.sound_data_path(blender_object.data)

        if blender_object.type == "LIGHT_PROBE":
            entity["size"] = blender_object.data.influence_distance
            entity["falloff"] = blender_object.data.falloff
            entity["intensity"] = blender_object.data.intensity
            entity["near"] = blender_object.data.clip_start
            entity["far"] = blender_object.data.clip_end

        if blender_object.active_material:
            entity["material"] = materials.material_path(blender_object.active_material)

        for blender_child in sorted(blender_object.children, key=lambda x: x.name):
            entity_child = write_entity(report, blender_child, directory)
            if entity_child:
                entity["children"].append(entity_path(blender_child))

        write_file(report, entity, directory, entity_path(blender_object))
        return entity


def entity_path(blender_object):
    collection = blender_object.instance_collection
    if collection:
        extension = blender_object.get("entity_type") or collection.get("entity_type") or get_type(blender_object)
    else:
        extension = blender_object.get("entity_type") or get_type(blender_object)
    return (library_path(blender_object) + "entities/" + str(blender_object.name) + '.' + str(extension)).strip('/')


def write(report, directory, objects):

    for entity in sorted(objects, key=lambda x: x.name):
        write_entity(report, entity, directory)
    report({'INFO'}, "Wrote all entities")

    materials.write(report, directory)
    meshes.write(report, directory, bpy.data.objects)
    spot_lights.write(report, directory)
    directional_lights.write(report, directory)
    sounds.write(report, directory)
