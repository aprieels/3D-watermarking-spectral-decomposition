
import utils
import numpy

import pymesh
from random import random

def noise(mesh, amplitude):
    new_vertices = []
    for vertice in mesh.vertices:
        new_vertices.append([vertice[0] + vertice[0] * random() * amplitude, vertice[1] + vertice[1] * random() * amplitude, vertice[2] + vertice[2] * random() * amplitude])

    return pymesh.form_mesh(numpy.array(new_vertices), mesh.faces)

def smoothing(mesh, iterations):
    neighbors, _ = utils.get_neighbors_and_valence(mesh.num_vertices, mesh.faces)
    vertices = mesh.vertices
    for _ in range(iterations):
        for i in range(mesh.num_vertices):
            new_value = compute_center(neighbors[i], vertices)
            vertices[i] = new_value

    return pymesh.form_mesh(vertices, mesh.faces)

def compute_center(points, vertices):
    x = 0.0
    y = 0.0
    z = 0.0

    for point in points:
        x += vertices[point][0]
        y += vertices[point][1]
        z += vertices[point][2]

    return [x/len(points), y/len(points), z/len(points)]