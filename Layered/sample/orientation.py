import numpy

def orient_mesh(vertices, axis):
    vector_norm = numpy.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
    yz_length = numpy.sqrt(axis[1]**2 + axis[2]**2)

    if vector_norm != 0:
        y_angle = numpy.arccos(yz_length/vector_norm)
        rotation_y = [[numpy.cos(y_angle), 0, numpy.sin(y_angle)], [0, 1, 0], [-numpy.sin(y_angle), 0, numpy.cos(y_angle)]] 
        vertices = numpy.dot(vertices, rotation_y)

    if yz_length != 0 :
        x_angle = numpy.arccos(axis[2]/yz_length)
        rotation_x = [[1, 0, 0], [0, numpy.cos(x_angle), -numpy.sin(x_angle)], [0, numpy.sin(x_angle), numpy.cos(x_angle)]] 
        vertices = numpy.dot(vertices, rotation_x)

    return vertices
    