import bpy
import bmesh
import struct
import json
from . import materials, models, meshes, lights

def write(dir, filepath, objects):
    blender_objects = [o for o in objects if not o.parent and o.type in {"MESH", "EMPTY"}]
    blender_objects = sorted(blender_objects, key=lambda x: x.name, reverse=False)

    directory = dir

    root = list()

    print("Writing level.")
    for blender_object in blender_objects:
        root.append(str(blender_object.name) + "." + str(blender_object.get("entity_type") or "model"))
    file = open(filepath, 'w')
    file.write(json.dumps(root))
    file.close()

    print("Writing models.")
    models.write(directory, objects)
    print("Writing materials.")
    materials.write(directory)
    print("Writing meshes.")
    meshes.write(directory, [o for o in objects if o.type == "MESH"])

    #print("Writing lamps.")
    #lights.write(directory)

    return {'FINISHED'}
