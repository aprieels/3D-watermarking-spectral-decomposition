
import subprocess
import os
import numpy as np
import pymesh

'''
    Partitions a mesh into a number of patches defined by @partitions using METIS
'''
def mesh_partitioning(filename, mesh, partitions):

    if partitions < 2:
        return [mesh], [range(mesh.num_vertices)]

    # Get only the name of the file (without its extension)
    filename, _ = os.path.splitext(filename)

    # Convert the mesh to a file of format "mesh" in order to apply METIS on it
    file = open(filename + '.mesh', 'w')
    file.write(str(len(mesh.faces)) + " " + str(1) + "\n")
    for f in mesh.faces:
        file.write(str(f[0]+1) + " " + str(f[1]+1) + " " + str(f[2]+1) + "\n")
    file.close()

    # Apply METIS on the file
    with open(os.devnull, "w") as f:
        subprocess.check_call(['mpmetis', filename + '.mesh', str(partitions)], stdout=f)

    # Read the file produced by METIS
    file = open(filename + '.mesh.epart.'+ str(partitions))
    partitions_list = file.readlines()

    patches = []
    mapping = []

    for i in range(partitions):
        faces = []
        vertices = []

        # Initialize all the mappings at -1
        indexes_mapping = np.zeros(mesh.num_vertices) - 1

        for j, partition in enumerate(partitions_list):

            # Find all the faces that should be added to this  specific patch
            if int(partition) == i:

                # Check if the vertices corresponding to this face have already been added to this parttion
                i1 = indexes_mapping[mesh.faces[j][0]]
                i2 = indexes_mapping[mesh.faces[j][1]]
                i3 = indexes_mapping[mesh.faces[j][2]]

                # If the vertices have not been added to this partition, add them and update the mapping
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

                # Add the faces to the list of faces for this partition with the correct indexes
                faces.append([i1, i2, i3])

        # Save the patch and the mapping
        mapping.append(indexes_mapping)
        patches.append(pymesh.form_mesh(np.array(vertices), np.array(faces)))

    return patches, mapping
    