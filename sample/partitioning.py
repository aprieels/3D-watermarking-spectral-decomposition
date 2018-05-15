
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

    max_z = numpy.max(vertices[:, 2]) + 0.00000001
    min_z = numpy.min(vertices[:, 2]) - 0.00000001

    interval_z = (max_z-min_z)/partitions

    cut_value = min_z + interval_z
    remaining_faces = faces

    already_computed_intersections = []

    for _ in range(partitions):

        patch, remaining_faces, vertices, already_computed_intersections = separate_vertices(remaining_faces, vertices, cut_value, initial_num_vertices, already_computed_intersections)
        cut_value += interval_z

        disconnected_meshes = split_disconnected_meshes(patch)

        for mesh_part in disconnected_meshes:
            patches.append(mesh_part)

    return patches


def separate_vertices(remaining_faces, vertices, cut_value, initial_num_vertices, already_computed_intersections):

    below = []
    below_vertices = []
    above = []
    intersections_above = []

    indexes_match = numpy.subtract(numpy.zeros(4*len(vertices)), 1)
    
    for face in remaining_faces:

        vertice1, index1, vertice2, index2, vertice3, index3 = sort_vertices(vertices, face)

        if vertice3[2] <= cut_value:

            # All the vertices are under the cut_value, this means that the whole face can be added to this partition (below)

            i1, below_vertices = find_index_or_add(face[0], indexes_match, below_vertices, vertices)
            i2, below_vertices = find_index_or_add(face[1], indexes_match, below_vertices, vertices)
            i3, below_vertices = find_index_or_add(face[2], indexes_match, below_vertices, vertices)

            below.append([i1, i2, i3])

        elif vertice2[2] < cut_value:

            # Only one of the vertices is above the cut_value, this means that the triangle must be divided into three smaller triangles:
            #   - One triangle is located above the cut_value and must be given to the next partition (above)
            #   - Two triangles are located under the cut value and belong to this partition (below)

            idx_inter1, vertices, new_intersection = compute_intersection(vertice3, vertice2, cut_value, vertices, initial_num_vertices, already_computed_intersections)
            if new_intersection is not None :
                already_computed_intersections.append(new_intersection)
                intersections_above.append(new_intersection)

            idx_inter2, vertices, new_intersection = compute_intersection(vertice3, vertice1, cut_value, vertices, initial_num_vertices, already_computed_intersections)
            if new_intersection is not None :
                already_computed_intersections.append(new_intersection)
                intersections_above.append(new_intersection)

            above.append([index3, idx_inter1, idx_inter2])

            i1, below_vertices = find_index_or_add(index1, indexes_match, below_vertices, vertices)
            i2, below_vertices = find_index_or_add(index2, indexes_match, below_vertices, vertices)
            below_idx_i1, below_vertices = find_index_or_add(idx_inter1, indexes_match, below_vertices, vertices)
            below_idx_i2, below_vertices = find_index_or_add(idx_inter2, indexes_match, below_vertices, vertices)

            below.append([below_idx_i1, below_idx_i2, i1])
            below.append([i1, i2, below_idx_i1])

        elif vertice1[2] < cut_value:

            # Two of the vertices are above the cut_value, this means that the triangle must be divided into three smaller triangles:
            #   - Two triangles are located above the cut_value and must be given to the next partition (above)
            #   - One triangle is located under the cut value and belongs to this partition (below)

            idx_inter1, vertices, new_intersection = compute_intersection(vertice1, vertice2, cut_value, vertices, initial_num_vertices, already_computed_intersections)
            if new_intersection is not None :
                already_computed_intersections.append(new_intersection)
                intersections_above.append(new_intersection)

            idx_inter2, vertices, new_intersection = compute_intersection(vertice1, vertice3, cut_value, vertices, initial_num_vertices, already_computed_intersections)
            if new_intersection is not None :
                already_computed_intersections.append(new_intersection)
                intersections_above.append(new_intersection)

            above.append([index2, index3, idx_inter2])
            above.append([index2, idx_inter1, idx_inter2])

            i1, below_vertices = find_index_or_add(index1, indexes_match, below_vertices, vertices)
            below_idx_i1, below_vertices = find_index_or_add(idx_inter1, indexes_match, below_vertices, vertices)
            below_idx_i2, below_vertices = find_index_or_add(idx_inter2, indexes_match, below_vertices, vertices)

            below.append([i1, below_idx_i1, below_idx_i2])

        else:

            # All the vertices are over the cut_value, this means that the face must be added to the next partition (above)

            above.append(face)

    patch = pymesh.form_mesh(numpy.array(below_vertices), numpy.array(below))

    return patch, above, vertices, intersections_above

def compute_intersection(vertice_1, vertice_2, cut_value, vertices, initial_num_vertices, already_computed_intersections):

    x1 = round((cut_value-vertice_1[2])*(vertice_2[0]-vertice_1[0])/(vertice_2[2]-vertice_1[2]) + vertice_1[0], 10)
    y1 = round((cut_value-vertice_1[2])*(vertice_2[1]-vertice_1[1])/(vertice_2[2]-vertice_1[2]) + vertice_1[1], 10)

    intersection = [x1, y1, cut_value]
    
    index = -1
    new_intersection = None

    for i in already_computed_intersections:
        if i[0][0] == intersection[0] and i[0][1] == intersection[1] and i[0][2] == intersection[2]:
            index = i[1]
            break
            
    if index == -1:
        vertices = numpy.concatenate((vertices, [intersection]))
        index = len(vertices)-1
        new_intersection = [intersection, index]

    return index, vertices, new_intersection


def find_index_or_add(n_vertice, indexes_match, new_vertices, vertices):
    idx = indexes_match[n_vertice]

    if (idx == -1):
        new_vertices.append(vertices[n_vertice])
        idx = len(new_vertices) - 1
        indexes_match[n_vertice] = idx

    return idx, new_vertices

def sort_vertices(vertices, face):
    v1, v2, v3 = sorted([[vertices[face[0]], face[0]], [vertices[face[1]], face[1]], [vertices[face[2]], face[2]]], key=getKey)
    return v1[0], v1[1], v2[0], v2[1], v3[0], v3[1]

def split_disconnected_meshes(mesh):

    connected_faces = []
    for _ in range(mesh.num_vertices):
        connected_faces.append([])

    for face in mesh.faces: 
        for i in range(3):
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

            i1, vertices = find_index_or_add(face[0], indexes_match, vertices, mesh.vertices)
            i2, vertices = find_index_or_add(face[1], indexes_match, vertices, mesh.vertices)
            i3, vertices = find_index_or_add(face[2], indexes_match, vertices, mesh.vertices)

            if [i1, i2, i3] not in faces:
                faces.append([i1, i2, i3])

            for i in range(3):
                if not connected[face[i]]:
                    connected[face[i]] = True
                    q.appendleft(face[i])

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

def merge(mesh_list):
    resulting_vertices = []
    resulting_faces = []

    count_vertices = 0

    for mesh in mesh_list:
        for vertice in mesh.vertices:
            resulting_vertices.append(vertice)
        for face in mesh.faces:
            resulting_faces.append(numpy.add(face, count_vertices))
        count_vertices += mesh.num_vertices

    merged_mesh = pymesh.form_mesh(numpy.array(resulting_vertices), numpy.array(resulting_faces))
    resulting_mesh, _ = pymesh.remove_duplicated_vertices(merged_mesh)

    return resulting_mesh