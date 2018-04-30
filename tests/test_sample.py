import random
import os
import pymesh
import numpy

from context import partitioning
from context import spectral_decomposition
from context import orientation

def insert_extract(filename_in = os.path.join(os.path.dirname(__file__), 'source_models/bunny.stl'), data = [random.randrange(2) for _ in range(64)], filename_out = os.path.join(os.path.dirname(__file__), 'watermarked_models/out.obj'), axis = [0, 0, 1], secret=123456, strength = 10, min_vertices = 0):

    print 'Data to be inserted: ', data

    spectral_decomposition.insert(filename_in, filename_out, data, axis, secret, strength, min_vertices)
    data_retrieved = spectral_decomposition.extract(filename_out, secret, 64, strength, min_vertices)

    n_errors = len([x for x, y in zip(data, data_retrieved) if x != y])

    print 'Data retrieved: ', data_retrieved
    print 'Number of errors: ', n_errors

    return n_errors

def test_partitions():
    m = pymesh.load_mesh(os.path.join(os.path.dirname(__file__), './source_models/bunny.obj'))
    patches = partitioning.layers_partitioning(m.faces, m.vertices, 10) 
    i = 0
    for p in patches: 
        pymesh.save_mesh('test'+str(i)+'.obj', p)
        i += 1

def test_orientation():
    m = pymesh.load_mesh(os.path.join(os.path.dirname(__file__), 'source_models/bunny.obj'))
    new_mesh = orientation.orient_printed_mesh(m)
    #pymesh.save_mesh_raw(os.path.join(os.path.dirname(__file__), 'watermarked_models/out_orientation.obj'), new_vertices, m.faces)

if __name__ == '__main__':
    insert_extract()