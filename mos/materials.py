import bpy
import bmesh
import struct

def write(dir):
    materials = bpy.data.materials

    for material in materials:

        file = open(dir + '/' + material.name + '.material', 'bw')

        print('Exporting: ' + material.name)
        #ambient = tuple([material.ambient * c for c in material.diffuse_color])

        ambient = material.diffuse_color * material.ambient
        #print(ambient)
        diffuse = material.diffuse_color
        #print(diffuse)
        specular = material.specular_color
        #print(specular)
        opacity = material.alpha
        #print(opacity)
        specular_exponent = float(material.specular_hardness)

        file.write(struct.pack('fff', *ambient))
        file.write(struct.pack('fff', *diffuse))
        file.write(struct.pack('fff', *specular))
        file.write(struct.pack('f', opacity))
        file.write(struct.pack('f', specular_exponent))

        file.close()
        print("Wrote file: " + file.name)
