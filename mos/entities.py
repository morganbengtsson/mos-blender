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

    def write(self, directory):
        entity_type = self.type or "model"
        entity_file = open(directory + '/' + self.name + "." + entity_type, 'w')
        entity_file.write(json.dumps(self, cls=ObjectEncoder))
        entity_file.close()

    def file_name(self):
        return str(self.name) + "." + str(self.type)


def write_entity(blender_object, directory):
    if blender_object.type not in {"MESH", "EMPTY"}:
        print("Not supported")
    else:
        entity = Entity()

        entity.name = blender_object.name

        transform_matrix = blender_object.matrix_local

        transform = list()
        for row in transform_matrix.col:
            transform.extend(list(row))

        entity.transform = transform

        entity.type = blender_object.get("entity_type") or "model"

        entity.id = blender_object.as_pointer()

        if blender_object.type == "MESH":
            entity.mesh = mesh_name(blender_object)
            entity.mesh += ".mesh"

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
    meshes.write(directory, [o for o in bpy.data.objects if o.type == "MESH"])
