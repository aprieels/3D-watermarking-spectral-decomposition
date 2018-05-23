import random
import os
import sys
import pymesh
import numpy

from context import partitioning
from context import spectral_decomposition

def insert_extract(filename_in = os.path.join(os.path.dirname(__file__), 'source_models/bunny.ply'), data = [random.randrange(2) for _ in range(64)], filename_out = os.path.join(os.path.dirname(__file__), 'watermarked_models/out.obj'), axis = [0, 1, 0], secret=123456, i0 = 10, visual_distance = 2):

    print 'Data to be inserted: ', data

    spectral_decomposition.insert(filename_in, filename_out, data, axis, secret, i0, visual_distance)
    data_retrieved = spectral_decomposition.extract(filename_out, secret, 64, i0)

    n_errors = len([x for x, y in zip(data, data_retrieved) if x != y])

    print 'Data retrieved: ', data_retrieved
    print 'Number of errors: ', n_errors

    return n_errors

def test_partitions():
    m = pymesh.load_mesh(os.path.join(os.path.dirname(__file__), './source_models/bunny.stl'))
    patches, _ = partitioning.mesh_partitioning('./source_models/bunny.stl', m, 2) 

    for i, patch in enumerate(patches):
        pymesh.save_mesh('test'+str(i)+'.stl', patch)

if __name__ == '__main__':
    insert_extract()