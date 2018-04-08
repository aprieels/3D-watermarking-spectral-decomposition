
import subprocess
import os
import numpy
import pymesh
from collections import deque

def mesh_partitioning(filename, faces, partitions):

    if partitions < 2:
        return [faces]

    filename, _ = os.path.splitext(filename)

    file = open(filename + '.mesh', 'w')
    file.write(str(len(faces)) + " " + str(1) + "\n")
    for f in faces:
        file.write(str(f[0]+1) + " " + str(f[1]+1) + " " + str(f[2]+1) + "\n")
    file.close()

    with open(os.devnull, "w") as f:
        subprocess.check_call(['mpmetis', filename + '.mesh', str(partitions)], stdout=f)

    file = open(filename + '.mesh.epart.'+ str(partitions))
    lines = file.readlines()

    patches = []

    for i in range(partitions):
        patches.append([])

    for i in range(len(lines)):
        patches[int(lines[i])].append([faces[i][0], faces[i][1], faces[i][2]])

    return patches

def layers_partitioning(faces, vertices, partitions):

    initial_num_vertices = len(vertices)

    patches = []

    max_z = numpy.max(vertices[:, 2])
    min_z = numpy.min(vertices[:, 2])

    interval_z = (max_z-min_z)/partitions

    cut_value = min_z + interval_z
    remaining = faces

    for i in range(partitions):
        below = []
        below_vertices = []
        above = []
        indexes_match = numpy.subtract(numpy.zeros(4*len(vertices)), 1)
        
        for face in remaining:
            v1, v2, v3 = sorted([[vertices[face[0]], face[0]], [vertices[face[1]], face[1]], [vertices[face[2]], face[2]]], key=getKey)

            vertice1 = v1[0]
            index1 = v1[1]
            vertice2 = v2[0]
            index2 = v2[1]
            vertice3 = v3[0]
            index3 = v3[1]

            if vertice3[2] <= cut_value:
                i1 = indexes_match[face[0]]
                i2 = indexes_match[face[1]]
                i3 = indexes_match[face[2]]

                if (i1 == -1):
                    below_vertices.append(vertices[face[0]])
                    i1 = len(below_vertices) - 1
                    indexes_match[face[0]] = i1
                    
                if (i2 == -1):
                    below_vertices.append(vertices[face[1]])
                    i2 = len(below_vertices) - 1
                    indexes_match[face[1]] = i2

                if (i3 == -1):
                    below_vertices.append(vertices[face[2]])
                    i3 = len(below_vertices) - 1
                    indexes_match[face[2]] = i3

                below.append([i1, i2, i3])
            elif vertice2[2] < cut_value:
                x1 = round((cut_value-vertice3[2])*(vertice2[0]-vertice3[0])/(vertice2[2]-vertice3[2]) + vertice3[0], 10)
                y1 = round((cut_value-vertice3[2])*(vertice2[1]-vertice3[1])/(vertice2[2]-vertice3[2]) + vertice3[1], 10)
                intersection1 = [x1, y1, cut_value]
                idx_inter1 = -1

                for idx, vertice in enumerate(vertices[initial_num_vertices:]):
                    if vertice[0] == intersection1[0] and vertice[1] == intersection1[1] and vertice[2] == intersection1[2]:
                        idx_inter1 = initial_num_vertices + idx

                if idx_inter1 == -1:
                    vertices = numpy.concatenate((vertices, [intersection1]))
                    idx_inter1 = len(vertices)-1

                x2 = round((cut_value-vertice3[2])*(vertice1[0]-vertice3[0])/(vertice1[2]-vertice3[2]) + vertice3[0], 10)
                y2 = round((cut_value-vertice3[2])*(vertice1[1]-vertice3[1])/(vertice1[2]-vertice3[2]) + vertice3[1], 10)
                intersection2 = [x2, y2, cut_value]
                idx_inter2 = -1

                for idx, vertice in enumerate(vertices[initial_num_vertices:]):
                    if vertice[0] == intersection2[0] and vertice[1] == intersection2[1] and vertice[2] == intersection2[2]:
                        idx_inter2 = initial_num_vertices + idx

                if idx_inter2 == -1:
                    vertices = numpy.concatenate((vertices, [intersection2]))
                    idx_inter2 = len(vertices)-1

                above.append([index3, idx_inter1, idx_inter2])

                i1 = indexes_match[index1]
                i2 = indexes_match[index2]
                below_idx_i1 = indexes_match[idx_inter1]
                below_idx_i2 = indexes_match[idx_inter2]
                if (i1 == -1):
                    below_vertices.append(vertices[index1])
                    i1 = len(below_vertices) - 1
                    indexes_match[index1] = i1
                    
                if (i2 == -1):
                    below_vertices.append(vertices[index2])
                    i2 = len(below_vertices) - 1
                    indexes_match[index2] = i2
                
                if (below_idx_i1 == -1):
                    below_vertices.append(vertices[idx_inter1])
                    below_idx_i1 = len(below_vertices) - 1
                    indexes_match[idx_inter1] = below_idx_i1

                if (below_idx_i2 == -1):
                    below_vertices.append(vertices[idx_inter2])
                    below_idx_i2 = len(below_vertices) - 1
                    indexes_match[idx_inter2] = below_idx_i2

                below.append([below_idx_i1, below_idx_i2, i1])
                below.append([i1, i2, below_idx_i1])
            elif vertice1[2] < cut_value:
                x1 = round((cut_value-vertice1[2])*(vertice2[0]-vertice1[0])/(vertice2[2]-vertice1[2]) + vertice1[0], 10)
                y1 = round((cut_value-vertice1[2])*(vertice2[1]-vertice1[1])/(vertice2[2]-vertice1[2]) + vertice1[1], 10)
                intersection1 = [x1, y1, cut_value]
                idx_inter1 = -1

                for idx, vertice in enumerate(vertices[initial_num_vertices:]):
                    if vertice[0] == intersection1[0] and vertice[1] == intersection1[1] and vertice[2] == intersection1[2]:
                        idx_inter1 = initial_num_vertices + idx

                if idx_inter1 == -1:
                    vertices = numpy.concatenate((vertices, [intersection1]))
                    idx_inter1 = len(vertices)-1

                x2 = round((cut_value-vertice1[2])*(vertice3[0]-vertice1[0])/(vertice3[2]-vertice1[2]) + vertice1[0], 10)
                y2 = round((cut_value-vertice1[2])*(vertice3[1]-vertice1[1])/(vertice3[2]-vertice1[2]) + vertice1[1], 10)
                intersection2 = [x2, y2, cut_value]
                idx_inter2 = -1

                for idx, vertice in enumerate(vertices[initial_num_vertices:]):
                    if vertice[0] == intersection2[0] and vertice[1] == intersection2[1] and vertice[2] == intersection2[2]:
                        idx_inter2 = initial_num_vertices + idx

                if idx_inter2 == -1:
                    vertices = numpy.concatenate((vertices, [intersection2]))
                    idx_inter2 = len(vertices)-1

                above.append([index2, index3, idx_inter2])
                above.append([index2, idx_inter1, idx_inter2])

                i1 = indexes_match[index1]
                below_idx_i1 = indexes_match[idx_inter1]
                below_idx_i2 = indexes_match[idx_inter2]
                if (i1 == -1):
                    below_vertices.append(vertices[index1])
                    i1 = len(below_vertices) - 1
                    indexes_match[index1] = i1
                
                if (below_idx_i1 == -1):
                    below_vertices.append(vertices[idx_inter1])
                    below_idx_i1 = len(below_vertices) - 1
                    indexes_match[idx_inter1] = below_idx_i1

                if (below_idx_i2 == -1):
                    below_vertices.append(vertices[idx_inter2])
                    below_idx_i2 = len(below_vertices) - 1
                    indexes_match[idx_inter2] = below_idx_i2

                below.append([i1, below_idx_i1, below_idx_i2])
            else:
                above.append(face)
        cut_value += interval_z
        remaining = above
        disconnected_meshes = split_disconnected_meshes(pymesh.form_mesh(numpy.array(below_vertices), numpy.array(below)))

        if type(disconnected_meshes) is list:
            for mesh_part in disconnected_meshes:
                patches.append(mesh_part)
        else:
            patches.append(disconnected_meshes)

        #patches.append(pymesh.form_mesh(numpy.array(below_vertices), numpy.array(below)))

    return patches

def split_disconnected_meshes(mesh):

    connected_faces = []
    for i in range(mesh.num_vertices):
        connected_faces.append([])

    for face in mesh.faces: 
        for i in range(len(face)):
            connected_faces[face[i]].append(face)

    connected = numpy.zeros(mesh.num_vertices, dtype=bool)

    indexes_match = numpy.subtract(numpy.zeros(mesh.num_vertices), 1)

    vertices = []
    faces = []
    q = deque([mesh.faces[0][0]])
    connected[mesh.faces[0][0]] = True

    while len(q) > 0 :
        vertice = q.pop()
        for face in connected_faces[vertice]:
            i1 = indexes_match[face[0]]
            i2 = indexes_match[face[1]]
            i3 = indexes_match[face[2]]

            if (i1 == -1):
                vertices.append(mesh.vertices[face[0]])
                i1 = len(vertices) - 1
                indexes_match[face[0]] = i1
                
            if (i2 == -1):
                vertices.append(mesh.vertices[face[1]])
                i2 = len(vertices) - 1
                indexes_match[face[1]] = i2

            if (i3 == -1):
                vertices.append(mesh.vertices[face[2]])
                i3 = len(vertices) - 1
                indexes_match[face[2]] = i3

            faces.append([i1, i2, i3])
            for v in range(len(face)):
                if not connected[face[v]]:
                    connected[face[v]] = True
                    q.appendleft(face[v])

    resulting_mesh = pymesh.form_mesh(numpy.array(vertices), numpy.array(faces))

    remaining_faces = []

    for face in mesh.faces:
        if not connected[face[0]]:
            remaining_faces.append(face)

    meshes = [resulting_mesh]
    
    if len(remaining_faces) != 0:
        remaining_mesh = pymesh.form_mesh(numpy.array(mesh.vertices), numpy.array(remaining_faces))
        meshes.extend(split_disconnected_meshes(remaining_mesh))

    return meshes

def getKey(item):
    return item[0][2]