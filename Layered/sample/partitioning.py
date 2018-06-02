
import subprocess
import os
import numpy as np
import pymesh
from collections import deque

'''
    Partitions a mesh into a certain number of layers defined by @partitions
'''
def layers_partitioning(faces, vertices, partitions):

    initial_num_vertices = len(vertices)

    layers = []

    max_z = np.max(vertices[:, 2]) + 0.00000001
    min_z = np.min(vertices[:, 2]) - 0.00000001

    # Compute the interval
    interval_z = (max_z-min_z)/partitions

    # Compute the first cut_value
    cut_value = min_z + interval_z
    remaining_faces = faces

    already_computed_intersections = []

    for _ in range(partitions):

        # Separate the faces under the cut_value from the ones over than the cut_value
        patch, remaining_faces, vertices, already_computed_intersections = separate_vertices(remaining_faces, vertices, cut_value, initial_num_vertices, already_computed_intersections)
        
        #Compute the next cut_value
        cut_value += interval_z

        # Separate the resulting patch into separate components
        disconnected_meshes = split_disconnected_meshes(patch)

        # Add all the resulting meshes to the list of layers
        for mesh_part in disconnected_meshes:
            layers.append(mesh_part)

    return layers

'''
    Separate the faces in remaining_faces under the cut_value from the ones over the cut_value
'''
def separate_vertices(remaining_faces, vertices, cut_value, initial_num_vertices, already_computed_intersections):

    below = []
    below_vertices = []
    above = []
    intersections_above = []

    indexes_match = np.subtract(np.zeros(4*len(vertices)), 1)
    
    for face in remaining_faces:

        # sort the vertices in growing order and remember their initial position
        vertice1, index1, vertice2, index2, vertice3, index3 = sort_vertices(vertices, face)

        if vertice3[2] <= cut_value:

            # All the vertices are under the cut_value, this means that the whole face can be added to this partition (below)

            i1, below_vertices, indexes_match = find_index_or_add(face[0], indexes_match, below_vertices, vertices)
            i2, below_vertices, indexes_match = find_index_or_add(face[1], indexes_match, below_vertices, vertices)
            i3, below_vertices, indexes_match = find_index_or_add(face[2], indexes_match, below_vertices, vertices)

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

            i1, below_vertices, indexes_match = find_index_or_add(index1, indexes_match, below_vertices, vertices)
            i2, below_vertices, indexes_match = find_index_or_add(index2, indexes_match, below_vertices, vertices)
            below_idx_i1, below_vertices, indexes_match = find_index_or_add(idx_inter1, indexes_match, below_vertices, vertices)
            below_idx_i2, below_vertices, indexes_match = find_index_or_add(idx_inter2, indexes_match, below_vertices, vertices)

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

            i1, below_vertices, indexes_match = find_index_or_add(index1, indexes_match, below_vertices, vertices)
            below_idx_i1, below_vertices, indexes_match = find_index_or_add(idx_inter1, indexes_match, below_vertices, vertices)
            below_idx_i2, below_vertices, indexes_match = find_index_or_add(idx_inter2, indexes_match, below_vertices, vertices)

            below.append([i1, below_idx_i1, below_idx_i2])

        else:

            # All the vertices are over the cut_value, this means that the face must be added to the next partition (above)

            above.append(face)

    #Create the patch from the resulting faces
    patch = pymesh.form_mesh(np.array(below_vertices), np.array(below))

    return patch, above, vertices, intersections_above

'''
    Computes the intersection between the line going through @vertice_1 and @vertice_2 and the cut_value plane, returns it and saves it
'''
def compute_intersection(vertice_1, vertice_2, cut_value, vertices, initial_num_vertices, already_computed_intersections):

    # Compute the intersection
    x1 = round((cut_value-vertice_1[2])*(vertice_2[0]-vertice_1[0])/(vertice_2[2]-vertice_1[2]) + vertice_1[0], 10)
    y1 = round((cut_value-vertice_1[2])*(vertice_2[1]-vertice_1[1])/(vertice_2[2]-vertice_1[2]) + vertice_1[1], 10)
    intersection = [x1, y1, cut_value]
    
    index = -1
    new_intersection = None

    # Check if this intersection has already been computed so we need to use the index from the previous insertion in the list of vertices
    for i in already_computed_intersections:
        if i[0][0] == intersection[0] and i[0][1] == intersection[1] and i[0][2] == intersection[2]:
            index = i[1]
            break
            
    # Add the intersection to the list of vertices if it wasn't already there
    if index == -1:
        vertices = np.concatenate((vertices, [intersection]))
        index = len(vertices)-1
        new_intersection = [intersection, index]

    return index, vertices, new_intersection

'''
    Finds if a vertice from the original mesh has already been added to the list of vertices of the current layer and adds it if needed
'''
def find_index_or_add(n_vertice, indexes_match, new_vertices, vertices):
    idx = indexes_match[n_vertice]

    # If the vertice has not been added to the new layer, add it and save its new index
    if (idx == -1):
        new_vertices.append(vertices[n_vertice])
        idx = len(new_vertices) - 1
        indexes_match[n_vertice] = idx

    return idx, new_vertices, indexes_match

''' 
    Sorts the vertices in growing order
'''
def sort_vertices(vertices, face):
    v1, v2, v3 = sorted([[vertices[face[0]], face[0]], [vertices[face[1]], face[1]], [vertices[face[2]], face[2]]], key=get_key)
    return v1[0], v1[1], v2[0], v2[1], v3[0], v3[1]

'''
    Splits the disconnected submeshes inside a layer
'''
def split_disconnected_meshes(mesh):

    connected_faces = []
    for _ in range(mesh.num_vertices):
        connected_faces.append([])

    for face in mesh.faces: 
        for i in range(3):
            connected_faces[face[i]].append(face)

    connected = np.zeros(mesh.num_vertices, dtype=bool)

    indexes_match = np.subtract(np.zeros(mesh.num_vertices), 1)

    vertices = []
    faces = []
    # Add a first face to the list of conneccted faces
    q = deque([mesh.faces[0][0]])
    connected[mesh.faces[0][0]] = True

    # Perform a Breadth-First-Search on the faces
    while len(q) > 0 :
        vertice = q.pop()
        for face in connected_faces[vertice]:

            i1, vertices, indexes_match = find_index_or_add(face[0], indexes_match, vertices, mesh.vertices)
            i2, vertices, indexes_match = find_index_or_add(face[1], indexes_match, vertices, mesh.vertices)
            i3, vertices, indexes_match = find_index_or_add(face[2], indexes_match, vertices, mesh.vertices)

            if [i1, i2, i3] not in faces:
                faces.append([i1, i2, i3])

            for i in range(3):
                if not connected[face[i]]:
                    connected[face[i]] = True
                    q.appendleft(face[i])

    # Get on sub-mesh where all the faces are connected
    resulting_mesh = pymesh.form_mesh(np.array(vertices), np.array(faces))

    remaining_faces = []

    # List all the faces that do not belong to this specific sub-mesh
    for face in mesh.faces:
        if not connected[face[0]]:
            remaining_faces.append(face)

    meshes = [resulting_mesh]
    
    # If there are still faces that have not been considered restart the process only on those faces
    if len(remaining_faces) != 0:
        remaining_mesh = pymesh.form_mesh(np.array(mesh.vertices), np.array(remaining_faces))
        meshes.extend(split_disconnected_meshes(remaining_mesh))

    return meshes

def get_key(item):
    return item[0][2]

'''
    Merges all the meshes present in the list into a single one
'''
def merge(mesh_list):
    resulting_vertices = []
    resulting_faces = []

    count_vertices = 0

    # Add all the faces and all the vertices from the next patch to the resulting mesh
    for mesh in mesh_list:
        for vertice in mesh.vertices:
            resulting_vertices.append(vertice)
        for face in mesh.faces:
            resulting_faces.append(np.add(face, count_vertices))
        count_vertices += mesh.num_vertices

    merged_mesh = pymesh.form_mesh(np.array(resulting_vertices), np.array(resulting_faces))
    resulting_mesh, _ = pymesh.remove_duplicated_vertices(merged_mesh)

    return resulting_mesh