
import subprocess
import os
import numpy
import pymesh

def mesh_partitioning(filename, mesh, partitions):

    if partitions < 2:
        return [mesh], [range(mesh.num_vertices)]

    filename, _ = os.path.splitext(filename)

    file = open(filename + '.mesh', 'w')
    file.write(str(len(mesh.faces)) + " " + str(1) + "\n")
    for f in mesh.faces:
        file.write(str(f[0]+1) + " " + str(f[1]+1) + " " + str(f[2]+1) + "\n")
    file.close()

    with open(os.devnull, "w") as f:
        subprocess.check_call(['mpmetis', filename + '.mesh', str(partitions)], stdout=f)

    file = open(filename + '.mesh.epart.'+ str(partitions))
    lines = file.readlines()

    patches = []
    mapping = []

    for i in range(partitions):
        faces = []
        vertices = []
        indexes_mapping = numpy.zeros(mesh.num_vertices) - 1

        for j, line in enumerate(lines):

            if int(line) == i:

                i1 = indexes_mapping[mesh.faces[j][0]]
                i2 = indexes_mapping[mesh.faces[j][1]]
                i3 = indexes_mapping[mesh.faces[j][2]]

                if i1 == -1 :
                    vertices.append(mesh.vertices[mesh.faces[j][0]])
                    i1 = len(vertices) - 1
                    indexes_mapping[mesh.faces[j][0]] = i1
                if i2 == -1 :
                    vertices.append(mesh.vertices[mesh.faces[j][1]])
                    i2 = len(vertices) - 1
                    indexes_mapping[mesh.faces[j][1]] = i2
                if i3 == -1 :
                    vertices.append(mesh.vertices[mesh.faces[j][2]])
                    i3 = len(vertices) - 1
                    indexes_mapping[mesh.faces[j][2]] = i3

                faces.append([i1, i2, i3])

        mapping.append(indexes_mapping)
        patches.append(pymesh.form_mesh(numpy.array(vertices), numpy.array(faces)))

    return patches, mapping
    