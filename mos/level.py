import bpy
import bmesh
import struct
import json
from . import materials, entities, meshes, light_data


def write(dir, filepath, objects):
    blender_objects = [o for o in objects if not o.parent and o.type in {"MESH", "EMPTY"}]
    blender_objects = sorted(blender_objects, key=lambda x: x.name, reverse=False)

    print("Writing level.")
    root = list()
    for blender_object in blender_objects:
        root.append(str(blender_object.name) + "." + str(blender_object.get("entity_type") or "model"))
    level_file = open(filepath, 'w')
    level_file.write(json.dumps(root))
    level_file.close()

    print("Writing models.")
    entities.write(dir, objects)
    print("Writing materials.")
    materials.write(dir)
    print("Writing meshes.")
    meshes.write(dir, [o for o in objects if o.type == "MESH"])

    #print("Writing lamps.")
    #lights.write(directory)

    return {'FINISHED'}
