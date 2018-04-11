import random
import os
import pymesh
import numpy

from context import partitioning
from context import spectral_decomposition

def insert_extract(filename_in = os.path.join(os.path.dirname(__file__), 'source_models/bunny.obj'), data = [random.randrange(2) for _ in range(64)], filename_out = os.path.join(os.path.dirname(__file__), 'watermarked_models/out.obj'), secret=123456, i0 = 50):

    print data

    spectral_decomposition.insert(filename_in, filename_out, data, secret, i0)
    print 'embedded'
    data_retrieved = spectral_decomposition.extract(filename_out, secret, 64, i0)

    n_errors = len([x for x, y in zip(data, data_retrieved) if x != y])

    print data_retrieved
    print n_errors

    return n_errors

def test_partitions():
    m = pymesh.load_mesh('./source_models/venus_full.stl')
    patches = partitioning.layers_partitioning(m.faces, m.vertices, 10) 
    i = 0
    for p in patches: 
        pymesh.save_mesh('test'+str(i)+'.obj', p)
        i += 1

if __name__ == '__main__':
    insert_extract()