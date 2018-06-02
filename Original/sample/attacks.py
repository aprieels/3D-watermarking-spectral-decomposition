
import utils
import numpy

import pymesh
from random import random

'''
    Returns a copy of the mesh given as argument where noise (proportional to @amplitude) has been added to all the coordinates
'''
def noise(mesh, amplitude):
    new_vertices = []

    # Go through each vertice and modify each of its 3  coordinates relatively to @amplitude
    for vertice in mesh.vertices:
        new_vertices.append([vertice[0] + vertice[0] * random() * amplitude, vertice[1] + vertice[1] * random() * amplitude, vertice[2] + vertice[2] * random() * amplitude])

    return pymesh.form_mesh(numpy.array(new_vertices), mesh.faces)

'''
    Returns a smoothed copy of the mesh given as argument
'''
def smoothing(mesh, iterations):
    neighbors, _ = utils.get_neighbors_and_valence(mesh.num_vertices, mesh.faces)
    vertices = mesh.vertices

    # At each iteration, move each vertice to the center of its neighbors
    for _ in range(iterations):
        for i in range(mesh.num_vertices):
            new_value = compute_center(neighbors[i], vertices)
            vertices[i] = new_value

    return pymesh.form_mesh(vertices, mesh.faces)

'''
    Computes the center of gravity of a list of coordinates
'''
def compute_center(points, vertices):
    x = 0.0
    y = 0.0
    z = 0.0

    for point in points:
        x += vertices[point][0]
        y += vertices[point][1]
        z += vertices[point][2]

    return [x/len(points), y/len(points), z/len(points)]