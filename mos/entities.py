import json
import bpy
import idprop

from . import materials, meshes, light_data, sounds
from .common import *


type_map = {
  "MESH": "model",
  "EMTPY": "model",
  "LIGHT": "light",
  "SPEAKER": "sound",
  "CAMERA": "camera",
}


def get_type(blender_type):
    return type_map.get(blender_type) or "model"


def write_file(report, entity, directory, filepath):
    path = directory + '/' + filepath
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entity_file = open(path, 'w')
    entity_file.write(json.dumps(entity))
    entity_file.close()
    report({'INFO'}, "Wrote: " + path)


def write_entity(report, blender_object, directory):
    if blender_object.type not in {"MESH", "EMPTY", "LIGHT", "SPEAKER", "CAMERA"}:
        report({'INFO'}, "Object type: %s, not supported" % blender_object.type)
    else:
        entity = dict()
        entity["name"] = None
        entity["transform"] = [1, 0, 0, 0,
                          0, 1, 0, 0,
                          0, 0, 1, 0,
                          0, 0, 0, 1]
        entity["mesh"] = None
        entity["material"] = None
        entity["sound"] = None
        entity["children"] = list()
        entity["type"] = "model"
        entity["id"] = None
        entity["light"] = None

        keys = blender_object.keys()
        for key in keys:
            if not key.startswith("_") and not key.startswith("cycles"):
                if type(blender_object[key]) is idprop.types.IDPropertyArray:
                    entity[key] = list(blender_object[key])
                else:
                    entity[key] = blender_object[key]

        entity["name"] = blender_object.name

        transform_matrix = blender_object.matrix_local

        transform = list()
        for row in transform_matrix.col:
            transform.extend(list(row))

        entity["transform"] = transform

        collection = blender_object.instance_collection
        if collection:
            for group_object in sorted(collection.objects, key=lambda x: x.name):
                if not group_object.parent:
                    entity_child = write_entity(report, group_object, directory)
                    if entity_child:
                        entity["children"].append(entity_path(group_object))

        extension = get_type(blender_object.type)

        entity["type"] = blender_object.get("entity_type") or extension

        entity["id"] = blender_object.as_pointer()

        if entity["type"] == "environment_light":
            entity["extent"] = blender_object.empty_display_size

        if entity["type"] == "camera":
            scene = bpy.context.scene
            aspect = scene.render.resolution_x / scene.render.resolution_y

            entity["aspect"] = aspect

            projection_matrix = blender_object.calc_matrix_camera(depsgraph=bpy.context.evaluated_depsgraph_get(), scale_x=aspect)

            transform = list()
            for row in projection_matrix.col:
                transform.extend(list(row))
            entity["projection"] = transform
            focus_distance = (blender_object.data.dof.focus_object.location - blender_object.location).length if blender_object.data.dof.focus_object else blender_object.data.dof.focus_distance
            entity["focus_distance"] = focus_distance

        if blender_object.type == "MESH":
            entity["mesh"] = meshes.mesh_path(blender_object)

        if blender_object.type == "LIGHT":
            entity["light"] = light_data.light_data_path(blender_object.data)

        if blender_object.type == "SPEAKER":
            entity["sound"] = sounds.sound_data_path(blender_object.data)

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
        extension = blender_object.get("entity_type") or collection.get("entity_type") or get_type(blender_object.type)
    else:
        extension = blender_object.get("entity_type") or get_type(blender_object.type)
    return (library_path(blender_object) + "entities/" + str(blender_object.name) + '.' + str(extension)).strip('/')


def write(report, directory, objects):

    for entity in sorted(objects, key=lambda x: x.name):
        write_entity(report, entity, directory)
    report({'INFO'}, "Wrote all entities")

    materials.write(report, directory)
    meshes.write(report, directory, bpy.data.objects)
    light_data.write(report, directory)
    sounds.write(report, directory)
