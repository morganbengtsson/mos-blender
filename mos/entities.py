import json
import bpy
import idprop
import os

from . import materials, meshes, light_data, speakers
from .common import *


def get_type(blender_type):
    return "model" if blender_type in {"MESH", "EMPTY"} else "light" if blender_type == "LIGHT" else "speaker" if blender_type == "SPEAKER" else "model"


def write_file(entity, directory, filepath):
    path = directory + '/' + filepath
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entity_file = open(path, 'w')
    entity_file.write(json.dumps(entity))
    entity_file.close()
    print("Wrote: " + path)


def write_entity(blender_object, directory):
    if blender_object.type not in {"MESH", "EMPTY", "LIGHT", "SPEAKER"}:
        print("Not supported")
    else:
        entity = dict()
        entity["name"] = None
        entity["transform"] = [1, 0, 0, 0,
                          0, 1, 0, 0,
                          0, 0, 1, 0,
                          0, 0, 0, 1]
        entity["mesh"] = None
        entity["material"] = None
        entity["speaker"] = None
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

        # group = blender_object.dupli_group
        # TODO: Rename group
        group = blender_object.instance_collection
        if group:
            for group_object in sorted(group.objects, key=lambda x: x.name):
                if not group_object.parent:
                    entity_child = write_entity(group_object, directory)
                    if entity_child:
                        entity["children"].append(entity_path(group_object))

        extension = get_type(blender_object.type)

        entity["type"] = blender_object.get("entity_type") or extension

        entity["id"] = blender_object.as_pointer()

        if entity["type"] == "environment_light":
            entity["extent"] = blender_object.empty_display_size

        if blender_object.type == "MESH":
            entity["mesh"] = meshes.mesh_path(blender_object)

        if blender_object.type == "LIGHT":
            entity["light"] = light_data.light_data_path(blender_object.data)

        if blender_object.type == "SPEAKER":
            entity["speaker"] = speakers.speaker_data_path(blender_object.data)

        if blender_object.active_material:
            entity["material"] = materials.material_path(blender_object.active_material)

        for blender_child in sorted(blender_object.children, key=lambda x: x.name):
            entity_child = write_entity(blender_child, directory)
            if entity_child:
                entity["children"].append(entity_path(blender_child))

        write_file(entity, directory, entity_path(blender_object))
        return entity


def entity_path(blender_object):
    t = get_type(blender_object.type)
    extension = blender_object.get("entity_type") or t
    return (library_path(blender_object) + "entities/" + str(blender_object.name) + '.' + str(extension)).strip('/')


def write(directory, objects):
    print("Writing entities.")
    for entity in sorted(objects, key=lambda x: x.name):
        write_entity(entity, directory)

    materials.write(directory)
    meshes.write(directory, bpy.data.objects)
    light_data.write(directory)
    speakers.write(directory)
