import numpy
from scipy import spatial

import utils

def rms_error(original_mesh, watermarked_mesh):
    if original_mesh.num_vertices != watermarked_mesh.num_vertices:
        return -1 
    squared_dist = numpy.sum((original_mesh.vertices - watermarked_mesh.vertices)**2, axis=0)
    dist = numpy.sqrt(squared_dist)

    return dist

def local_smoothness(original_mesh, watermarked_mesh):
    if original_mesh.num_vertices != watermarked_mesh.num_vertices:
        return -1 

    epsilon = 1e-15
    neighbors, _ = utils.get_neighbors_and_valence(original_mesh.num_vertices, original_mesh.faces)

    original_numerator_sum = 0
    watermarked_numerator_sum = 0
    original_denominator_sum = 0
    watermarked_denominator_sum = 0

    distance_GL_sum = 0
    distance_sum = 0

    for i in range(original_mesh.num_vertices):
        original_coordinates = original_mesh.vertices[i]
        watermarked_coordinates = watermarked_mesh.vertices[i]

        for n in neighbors[i]:
            original_neighbor = original_mesh.vertices[n]
            watermarked_neighbor = watermarked_mesh.vertices[n]

            original_distance = max(spatial.distance.euclidean(original_coordinates, original_neighbor), epsilon)
            watermarked_distance = max(spatial.distance.euclidean(watermarked_coordinates, watermarked_neighbor), epsilon)

            original_numerator_sum += original_neighbor/original_distance
            original_denominator_sum += 1.0/original_distance

            watermarked_numerator_sum += watermarked_neighbor/watermarked_distance
            watermarked_denominator_sum += 1.0/watermarked_distance

        GL_original = original_coordinates - (original_numerator_sum/original_denominator_sum)
        GL_watermarked = watermarked_coordinates - (watermarked_numerator_sum/watermarked_denominator_sum)

        distance_GL_sum += spatial.distance.euclidean(GL_original, GL_watermarked)
        distance_sum += spatial.distance.euclidean(original_coordinates, watermarked_coordinates)
    
    return (distance_GL_sum + distance_sum)/(2*original_mesh.num_vertices)


def hausdorff_distance(original_mesh, watermarked_mesh):
    if original_mesh.num_vertices != watermarked_mesh.num_vertices:
        return -1 

    d1 = 0
    d2 = 0

    original_tree = spatial.KDTree(original_mesh.vertices)
    watermarked_tree = spatial.KDTree(watermarked_mesh.vertices)

    for vertice in original_mesh.vertices:
        closest_point = watermarked_mesh.vertices[watermarked_tree.query(vertice)[1]]
        dist = spatial.distance.euclidean(vertice, closest_point)
        d1 = max(d1, dist)

    for vertice in watermarked_mesh.vertices:
        closest_point = original_mesh.vertices[original_tree.query(vertice)[1]]
        dist = spatial.distance.euclidean(vertice, closest_point)
        d2 = max(d2, dist)

    return max(d1, d2)