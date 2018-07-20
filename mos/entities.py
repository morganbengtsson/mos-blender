import json
import bpy
import idprop
import os

from . import materials, meshes, light_data


def mesh_name(blender_object):
    name = ""
    if blender_object.library:
        library, file_extension = os.path.splitext(blender_object.library.filepath)
        name += library + '/'
    name += blender_object.data.name
    for modifier in blender_object.modifiers:
        name += "_" + modifier.name
    return name


def write_file(entity, directory):
    entity_file = open(directory + '/' + entity["name"] + "." + entity["type"], 'w')
    entity_file.write(json.dumps(entity))
    entity_file.close()


def file_name(entity):
    return str(entity["name"] + "." + str(entity["type"]))


def write_entity(blender_object, directory):
    if blender_object.type not in {"MESH", "EMPTY", "LAMP"}:
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

        group = blender_object.dupli_group
        if group:
            for group_object in group.objects:
                if not group_object.parent:
                    print("group obj: " + group_object.name)
                    entity_child = write_entity(group_object, directory)
                    if entity_child:
                        entity["children"].append(file_name(entity_child))

        extension = "model" if blender_object.type in {"MESH", "EMPTY"} else "light" if blender_object.type == "LAMP" else "model"

        entity["type"] = blender_object.get("entity_type") or extension

        entity["id"] = blender_object.as_pointer()

        if entity["type"] == "environment_light":
            entity["extent"] = blender_object.empty_draw_size

        if blender_object.type == "MESH":
            entity["mesh"] = mesh_name(blender_object)
            entity["mesh"] += ".mesh"

        if blender_object.type == "LAMP":
            entity["light"] = blender_object.data.name + ".light_data"

        if blender_object.active_material:
            entity["material"] = str(blender_object.active_material.name + ".material")

        for blender_child in blender_object.children:
            entity_child = write_entity(blender_child, directory)
            if entity_child:
                entity["children"].append(file_name(entity_child))

        write_file(entity, directory)
        return entity


def write(directory, objects):
    print("Writing entities/models.")
    for entity in objects:
        write_entity(entity, directory)

    print("Writing materials.")
    materials.write(directory)

    print("Writing meshes.")
    meshes.write(directory, bpy.data.objects)

    print("Writing light data.")
    light_data.write(directory)
