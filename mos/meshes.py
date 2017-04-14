import bpy
import bmesh
import struct
import json


def write_mesh_file(blender_object, write_dir, custom_file_name=None):
    try:
        name = blender_object.data.name
        for modifier in blender_object.modifiers:
            name += "_" + modifier.name
        mesh = blender_object.to_mesh(scene=bpy.context.scene,
                                      apply_modifiers=True,
                                      settings='PREVIEW')

        """
        if len(blender_object.modifiers) > 0:
            mesh = blender_object.to_mesh(scene=bpy.context.scene,
                                          apply_modifiers=True,
                                          settings='PREVIEW')
            name = blender_object.name
        else:
            mesh = blender_object.data

            #Todo fix mesh sharing!
            #name = mesh.name
            name = blender_object.name
            """

        mesh_type = blender_object.data.get("mesh_type")
    except:
        raise RuntimeError("Error in object " + blender_object.name)

    if mesh_type != "none":
        for index, slot in enumerate(blender_object.material_slots):
            if custom_file_name:
                filename = write_dir + '/' + custom_file_name
            else:
                filename = write_dir + '/' + name + ".mesh"
                if len(blender_object.material_slots) > 1:
                    filename = write_dir + '/' + name + "_" + str(index) + ".mesh"

            print('Exporting: ' + filename)
            print(mesh_type)

            bm = bmesh.new()
            bm.from_mesh(mesh)

            bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=2)

            indices = []
            positions = []
            normals = []
            tangents = []
            texture_uvs = []
            lightmap_uvs = []

            if len(mesh.uv_layers) >= 2:
                texture_uv_layer = bm.loops.layers.uv[0]
                lightmap_uv_layer = bm.loops.layers.uv[1]

                for face in bm.faces:
                    if face.material_index == index:
                        for loop in face.loops:
                            texture_uv = loop[texture_uv_layer].uv
                            texture_uv.y = 1.0 - texture_uv.y
                            lightmap_uv = loop[lightmap_uv_layer].uv
                            lightmap_uv.y = 1.0 - lightmap_uv.y
                            vert = loop.vert
                            positions.append(vert.co.to_tuple())
                            normals.append(vert.normal.to_tuple())
                            tangents.append(loop.calc_tangent().to_tuple())
                            texture_uvs.append(texture_uv.to_tuple())
                            lightmap_uvs.append(lightmap_uv.to_tuple())
            else:
                raise Exception(mesh.name + " must have two uv layers, with correct order. Texture first then lightmap ")
            bm.free()
            del bm

            mesh_file = open(filename, 'bw')

            # Header
            mesh_file.write(struct.pack('i', len(positions)))
            mesh_file.write(struct.pack('i', len(indices)))

            # Body
            for v in zip(positions, normals, tangents, texture_uvs, lightmap_uvs):
                mesh_file.write(struct.pack('fff', *v[0]))
                mesh_file.write(struct.pack('fff', *v[1]))
                mesh_file.write(struct.pack('fff', *v[2]))
                mesh_file.write(struct.pack('ff', *v[3]))
                mesh_file.write(struct.pack('ff', *v[4]))

            for i in indices:
                mesh_file.write(struct.pack('I', i))

            mesh_file.close()


def write(write_dir, objects):
    scene = bpy.context.scene

    objects = [o for o in objects if o.type == 'MESH']

    for blender_object in objects:
        write_mesh_file(blender_object, write_dir)
        print("Object: " + blender_object.name)
        if blender_object.find_armature():
            armature = blender_object.find_armature()
            for action in bpy.data.actions:
                animation = dict()
                animation["frame_rate"] = scene.render.fps
                animation["keyframes"] = list()
                armature.animation_data.action = action
                for index in range(scene.frame_start, scene.frame_end + 1, 2):
                    scene.frame_set(index)
                    mesh_name = blender_object.name + "_" + action.name.lower() + "_" + str(index) + ".mesh"
                    print(mesh_name)
                    write_mesh_file(blender_object, write_dir, mesh_name)
                    animation["keyframes"].append({"key": index, "mesh": mesh_name})

                animation_file = open(write_dir + '/' + blender_object.name + "_" + action.name.lower() + ".animation", 'w')
                animation_file.write(json.dumps(animation))
                animation_file.close()



