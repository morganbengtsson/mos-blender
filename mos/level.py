import bpy
import bmesh
import struct
import json
from . import entities, materials, models, meshes, lamps

def to_entity(directory, blender_object):
    entity_type = blender_object.get("entity_type")
    print("type: ", end=" ")
    print(entity_type)

    if not blender_object or blender_object.type not in {"MESH", "EMPTY", "CAMERA"}:
        return None
    if entity_type == "none":
        return None

    entity = dict()

    keys = blender_object.keys()
    for key in keys:
        if not key.startswith("_") and not key.startswith("cycles"):
            entity[key] = blender_object[key]

    entity['type'] = entity_type
    entity['name'] = blender_object.name

    m = blender_object.matrix_local
    location = [m[0][3], m[1][3], m[2][3]]

    entity['position'] = [location[0], location[1], location[2]]

    transform = list()
    for row in m.col:
        transform.extend(list(row))
    entity["transform"] = transform

    print("Writing models.")
    export_children = bool(blender_object.get("export_children"))
    print("children: " + str(export_children))
    #models.write(directory, [blender_object], True if entity_type is None else export_children)

    if blender_object.type in {"MESH", "EMPTY"}:
        entity["model"] = blender_object.name + ".model"
    entity["id"] = blender_object.as_pointer()

    return entity


def to_entities(directory, blender_objects):
    root = []
    for blender_object in blender_objects:
        level_object = to_entity(directory, blender_object)
        if level_object:
            level_object['children'] = to_entities(directory, blender_object.children)
            root.append(level_object)
    return root


def write(dir, filepath, objects):
    blender_objects = [o for o in objects if not o.parent and o.type in {"MESH", "EMPTY", "CAMERA"}]
    blender_objects = sorted(blender_objects, key=lambda x: x.name, reverse=False)

    directory = dir

    root = to_entities(directory, blender_objects)

    print("Writing entities.")
    file = open(filepath, 'w')
    file.write(json.dumps(root))
    file.close()

    print("Writing models.")
    models.write(directory, objects)

    print("Writing materials.")
    materials.write(directory)
    print("Writing meshes.")
    meshes.write(directory, [o for o in objects if o.type == "MESH"])
    print("Writing lamps.")
    lamps.write(directory)

    return {'FINISHED'}
