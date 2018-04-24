import json
from . import models, materials, meshes, lights

def to_entity(directory, blender_object):
    entity_type = blender_object.get("entity_type")
    print("type: ", end=" ")
    print(entity_type)

    if not blender_object or blender_object.type not in {"MESH", "EMPTY"}:
        return None

    if not blender_object.get("entity_type") and blender_object.parent:
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

    #print("Writing models.")
    #export_children = bool(blender_object.get("export_children"))
    #print("children: " + str(export_children))
    #models.write(directory, [blender_object], True if entity_type is None else export_children)
    print("WRITING " + blender_object.name)
    #models.write(directory, [blender_object], True)

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


def write(directory, objects):
    print("Writing entities.")
    root = to_entities(directory, objects)
    for entity in root:
        file = open(directory + '/' + entity["name"] + ".entity", 'w')
        file.write(json.dumps(entity))
        file.close()

    print("Writing models.")
    models.write(directory, objects)
    print("Writing materials.")
    materials.write(directory)
    print("Writing meshes.")
    meshes.write(directory, [o for o in objects if o.type == "MESH"])
    print("Writing lamps")
    lights.write(directory)
