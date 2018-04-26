import json
import bpy
from . import materials, meshes, light_data


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def mesh_name(blender_object):
    name = blender_object.data.name
    for modifier in blender_object.modifiers:
        name += "_" + modifier.name
    return name


class Entity(object):
    def __init__(self):
        self.name = None
        self.transform = [1, 0, 0, 0,
                          0, 1, 0, 0,
                          0, 0, 1, 0,
                          0, 0, 0, 1]
        self.mesh = None
        self.material = None
        self.children = list()
        self.type = "model"
        self.id = None
        self.light = None

    def write(self, directory):
        entity_type = self.type
        entity_file = open(directory + '/' + self.name + "." + entity_type, 'w')
        entity_file.write(json.dumps(self, cls=ObjectEncoder))
        entity_file.close()

    def file_name(self):
        return str(self.name) + "." + str(self.type)


def write_entity(blender_object, directory):
    if blender_object.type not in {"MESH", "EMPTY", "LAMP"}:
        print("Not supported")
    else:
        entity = Entity()

        keys = blender_object.keys()
        for key in keys:
            if not key.startswith("_") and not key.startswith("cycles"):
                setattr(entity, key, blender_object[key])

        entity.name = blender_object.name

        transform_matrix = blender_object.matrix_local

        transform = list()
        for row in transform_matrix.col:
            transform.extend(list(row))

        entity.transform = transform

        extension = "model" if blender_object.type in {"MESH", "EMPTY"} else "light" if blender_object.type == "LAMP" else "model"

        entity.type = blender_object.get("entity_type") or extension

        entity.id = blender_object.as_pointer()

        if blender_object.type == "MESH":
            entity.mesh = mesh_name(blender_object)
            entity.mesh += ".mesh"

        if blender_object.type == "LAMP":
            entity.light = blender_object.data.name + ".light_data"

        if blender_object.active_material:
            entity.material = str(blender_object.active_material.name + ".material")

        for blender_child in blender_object.children:
            entity_child = write_entity(blender_child, directory)
            if entity_child:
                entity.children.append(entity_child.file_name())

        entity.write(directory)
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
