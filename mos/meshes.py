import bpy
import struct
import os
import math


def round_3d(v):
    return round(v[0], 6), round(v[1], 6), round(v[2], 6)


def round_2d(v):
    return round(v[0], 6), round(v[1], 6)


def mesh_path(blender_object):
    name = blender_object.data.name
    if len(blender_object.modifiers) > 0:
        name = blender_object.name
    for modifier in blender_object.modifiers:
        name += "_" + modifier.name.lower()

    library = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))[0] + '/'
    if blender_object.data.library:
        library, file_extension = os.path.splitext(bpy.path.basename(blender_object.data.library.filepath))
        library = library + '/'
    path = library + "meshes/" + name + ".mesh"
    return path.strip('/')


def write_mesh_file(report, blender_object, write_dir):
    try:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        object_evaluated = blender_object.evaluated_get(depsgraph)
        mesh = object_evaluated.data

    except Exception as exception:
        raise Exception('Error while evaluating: ' + blender_object.name) from exception

    filepath = write_dir + '/' + mesh_path(blender_object)

    positions = []
    normals = []
    tangents = []
    texture_uvs = []
    groups = []
    weights = []

    faces = []
    vertex_indices_dict = {}
    vertex_count = 0

    if len(mesh.uv_layers) >= 1:
        mesh.calc_loop_triangles()
        for i, tri in enumerate(mesh.loop_triangles):
            temp_faces = []
            for j, vertex_index in enumerate(tri.vertices):
                position = round_3d(mesh.vertices[vertex_index].co.to_tuple())

                loop_index = tri.loops[j]
                texture_uv = list(round_2d(mesh.uv_layers[0].data[loop_index].uv))

                texture_uv[1] = 1.0 - texture_uv[1]
                texture_uv = tuple(texture_uv)
                
                vertex = mesh.vertices[vertex_index]
                bevel_weight = vertex.bevel_weight

                vertex_groups = [0, 0, 0, 0]
                vertex_weights = [0.0, 0.0, 0.0, 0.0]
                for k, group in enumerate(vertex.groups[:4]):
                    vertex_groups[k] = group.group
                    vertex_weights[k] = group.weight

                print(vertex_groups)
                print(vertex_weights)                

                key = mesh.vertices[vertex_index].index
                new_index = vertex_indices_dict.get(key)

                if tri.use_smooth:
                    if new_index is None or not(math.isclose(texture_uvs[new_index][0], texture_uv[0]) and math.isclose(texture_uvs[new_index][1], texture_uv[1])):
                        vertex_indices_dict[key] = vertex_count
                        positions.append(position)
                        normal = round_3d(mesh.vertices[vertex_index].normal)
                        normals.append(normal)
                        texture_uvs.append(texture_uv)
                        temp_faces.append(vertex_count)
                        tangents.append((0.0, 0.0, 0.0))
                        groups.append(vertex_groups)
                        weights.append(vertex_weights)
                        vertex_count += 1
                    else:
                        inx = vertex_indices_dict[key]
                        temp_faces.append(inx)
                else:
                    positions.append(position)
                    normal = round_3d(tri.normal.to_tuple())
                    normals.append(normal)
                    texture_uvs.append(texture_uv)
                    temp_faces.append(vertex_count)
                    tangents.append((0.0, 0.0, 0.0))
                    groups.append(vertex_groups)
                    weights.append(vertex_weights)
                    vertex_count += 1

            faces.append(temp_faces)

        indices = [val for sublist in faces for val in sublist]
    else:
        raise Exception(mesh.name + " must have one uv layer")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    mesh_file = open(filepath, 'bw')

    # Header
    mesh_file.write(struct.pack('i', len(positions)))
    mesh_file.write(struct.pack('i', len(indices)))

    # Body
    for vertex in zip(positions, normals, tangents, texture_uvs, groups, weights):
        mesh_file.write(struct.pack('fff', *vertex[0]))
        mesh_file.write(struct.pack('fff', *vertex[1]))
        mesh_file.write(struct.pack('fff', *vertex[2]))
        mesh_file.write(struct.pack('ff', *vertex[3]))
        mesh_file.write(struct.pack('iiii', *vertex[4]))
        mesh_file.write(struct.pack('ffff', *vertex[5]))


    for i in indices:
        mesh_file.write(struct.pack('I', i))

    mesh_file.close()
    report({'INFO'}, "Number of vertices: " + str(len(positions)))
    report({'INFO'}, "Number of indices: " + str(len(indices)))
    report({'INFO'}, "Wrote: " + filepath)


def write(report, write_dir, objects):
    objects = [o for o in objects if o.type == 'MESH']

    for blender_object in objects:
        write_mesh_file(report, blender_object, write_dir)
    report({'INFO'}, "Wrote all meshes.")
