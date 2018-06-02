import numpy as np

'''
    Reorient the mesh represented by @vertices so that the z-axis is aligned with @axis
'''
def orient_mesh(vertices, axis):
    vector_norm = np.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
    yz_length = np.sqrt(axis[1]**2 + axis[2]**2)

    # Rotate around the y-axis
    if vector_norm != 0:
        y_angle = np.arccos(yz_length/vector_norm)
        rotation_y = [[np.cos(y_angle), 0, np.sin(y_angle)], [0, 1, 0], [-np.sin(y_angle), 0, np.cos(y_angle)]] 
        vertices = np.dot(vertices, rotation_y)

    # Rotate around the x-axis
    if yz_length != 0 :
        x_angle = np.arccos(axis[2]/yz_length)
        rotation_x = [[1, 0, 0], [0, np.cos(x_angle), -np.sin(x_angle)], [0, np.sin(x_angle), np.cos(x_angle)]] 
        vertices = np.dot(vertices, rotation_x)

    return vertices
    