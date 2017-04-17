import json
import bpy
from . import materials, meshes


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def mesh_name(blender_object):
    name = blender_object.data.name
    for modifier in blender_object.modifiers:
        name += "_" + modifier.name
    return name


class Model(object):
    def __init__(self, name=None, transform=[1, 0, 0, 0,
                                             0, 1, 0, 0,
                                             0, 0, 1, 0,
                                             0, 0, 0, 1], mesh=None,
                 material=None, lit=True, models=list()):
        self.name = name
        self.transform = transform
        self.mesh = mesh
        self.material = material
        self.lit = lit
        self.models = models

    @classmethod
    def from_blender_object(cls, blender_object, force):
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

        model = Model()

        model.name = blender_object.name

        transform_matrix = blender_object.matrix_local

        transform = list()
        for row in transform_matrix.col:
            transform.extend(list(row))

        model.transform = transform

        print(len(blender_object.material_slots))

        if blender_object.type == "MESH":
            model.mesh = mesh_name(blender_object)
            model.mesh += ".mesh"

        if blender_object.active_material:
            model.material = str(blender_object.active_material.name + ".material")

        if blender_object.get("lit") is not None:
            model.lit = bool(blender_object.get("lit"))

        return model


def to_models(blender_objects, force):
    root = []
    for object in blender_objects:
        model = Model.from_blender_object(object, force)
        if model:
            #model.models.extend(to_models(object.children, force))
            model.models = model.models + to_models(object.children, force)
            root.append(model)
    return root


def write(directory, objects, force=False):
    print("Writing models.")
    models = to_models(objects, force)
    for model in models:
        file = open(directory + '/' + model.name + ".model", 'w')
        file.write(json.dumps(model, cls=ObjectEncoder))
        file.close()

    print("Writing materials.")
    materials.write(directory)
    print("Writing meshes.")
    meshes.write(directory, [o for o in bpy.data.objects if o.type == "MESH"])
