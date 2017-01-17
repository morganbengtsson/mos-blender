import json
import bpy
from . import materials, meshes


def to_model(blender_object, force):
    if not blender_object:
        return None

    if blender_object.get("export_model") in {"0", "False", "false", 0}:
        return None

    if blender_object.type not in {"MESH", "EMPTY"}:
        return None

    if blender_object.parent is not None and not force:
        if blender_object.get("entity_type") is not None:
            return None

    print("---")
    print("Exporting: " + blender_object.name)
    print("Type: " + blender_object.type)
    print("Entity type: " + str(blender_object.get("entity_type")))
    print("Parent: " + str(blender_object.parent))
    model = dict()
    model['name'] = blender_object.name

    m = blender_object.matrix_local
    location = [m[0][3], m[1][3], m[2][3]]

    transform = list()
    for row in m.col:
        transform.extend(list(row))

    model["transform"] = transform

    if blender_object.type == "MESH":
        model["mesh"] = blender_object.data.name
        for modifier in blender_object.modifiers:
            model["mesh"] += "_" + modifier.name
        model['mesh'] += ".mesh"

    if blender_object.active_material:
        model['material'] = str(blender_object.active_material.name + ".material")

    if blender_object.get("lit") is not None:
        model["lit"] = bool(blender_object.get("lit"))

    return model


def to_models(blender_objects, force):
    root = []
    for object in blender_objects:
        model = to_model(object, force)
        if model:
            model['models'] = to_models(object.children, force)
            root.append(model)
    return root


def write(directory, objects, force = False):
    print("Writing models.")
    models = to_models(objects, force)
    for model in models:
        file = open(directory + '/' + model["name"] + ".model", 'w')
        file.write(json.dumps(model))
        file.close()

    print("Writing materials.")
    materials.write(directory)
    print("Writing meshes.")
    meshes.write(directory, [o for o in bpy.data.objects if o.type == "MESH"])
