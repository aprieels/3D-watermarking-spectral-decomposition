import numpy
import pymesh
import embedding
import retrieval
import partitioning
import random
import utils
import distortion
import sys

def insert(filename_in, filename_out = 'out.obj', data = 32*[0, 1], axis = [0, 0, 1], secret = 123456, i0 = 100, visual_distance = sys.maxint):

    print
    print '########## Embedding started ##########'

    scrambled_data = scramble(data, secret)

    mesh = pymesh.load_mesh(filename_in)

    partitions = mesh.num_vertices/500
    patches, mapping = partitioning.mesh_partitioning(filename_in, mesh, partitions)

    print 'Step 1: Mesh patched'

    processed = 0
    bits_inserted = 0
    updated_vertices = []

    utils.progress(processed, len(patches), 'Inserting data in patches...')

    for patch in patches:

        B = compute_laplacian_matrix(patch.num_vertices, patch.faces)

        P = numpy.matmul(B, patch.vertices[:, 0])
        Q = numpy.matmul(B, patch.vertices[:, 1])
        R = numpy.matmul(B, patch.vertices[:, 2])

        P, Q, R, count = embedding.write(P, Q, R, scrambled_data, i0)

        BM1 = numpy.linalg.pinv(B)

        new_vertices = numpy.zeros((patch.num_vertices, 3))

        new_vertices[:, 0] = numpy.matmul(BM1, P)
        new_vertices[:, 1] = numpy.matmul(BM1, Q)
        new_vertices[:, 2] = numpy.matmul(BM1, R)
        
        updated_vertices.append(pymesh.form_mesh(new_vertices, patch.faces))

        bits_inserted = max(bits_inserted, count)

        processed += 1
        utils.progress(processed, len(patches), 'Inserting data in patches...')

    print
    print 'Step 2: Data inserted'

    if bits_inserted < len(data):
        print 'Only %s bits inserted, the bit error rate when retriving data might be significant' % (bits_inserted)

    new_vertices = numpy.zeros((mesh.num_vertices, 3))

    for i in range(mesh.num_vertices):
        for j in range(partitions):
            val = mapping[j][i]
            if val != -1:
                new_vertices[i] = updated_vertices[j].vertices[int(val)]
                continue
        
    pymesh.save_mesh(filename_out, pymesh.form_mesh(new_vertices, mesh.faces))

    print '########## Embedding finished ##########'
    print
    
def extract(filename, secret = 123456, length = 64, i0=100):

    print
    print '########## Retrieval started ##########'

    mesh = pymesh.load_mesh(filename)

    patches, _ = partitioning.mesh_partitioning(filename, mesh, mesh.num_vertices/500)

    print 'Step 1: Mesh patched'

    data = []

    processed = 0
    utils.progress(processed, len(patches), 'Reading data from patches...')

    for patch in patches:
        
        B = compute_laplacian_matrix(patch.num_vertices, patch.faces)

        P = numpy.matmul(B, patch.vertices[:, 0])
        Q = numpy.matmul(B, patch.vertices[:, 1])
        R = numpy.matmul(B, patch.vertices[:, 2])

        data.append(retrieval.read(P, Q, R, i0))

        processed += 1
        utils.progress(processed, len(patches), 'Reading data from patches...')

    print
    print 'Step 2: Data retrieved'

    final_data = unscramble(data_majority(data, length), secret)

    print '########## Retrieval finished ##########'
    print

    return final_data

def data_majority(data, length):
    final_data = numpy.zeros(length)
    for i in range(length):
        sum = 0.0
        count = 0
        for d in data:
            j = i
            while j < len(d):
                sum += d[j]
                count += 1
                j += length
        if count > 0:
            final_data[i] = round(sum/count)
    return final_data

def compute_laplacian_matrix (num_vertices, patch):

    laplacian = numpy.zeros((num_vertices, num_vertices))

    star, d = utils.get_neighbors_and_valence(num_vertices, patch)

    for i in range(num_vertices):
        laplacian[i][i] = 1
        for j in star[i]:
            laplacian[i][int(j)] = -1.0/d[i]
            
    eigenValues, eigenVectors = numpy.linalg.eig(laplacian)

    idx = eigenValues.argsort()
    eigenValues = eigenValues[idx]
    eigenVectors = eigenVectors[:,idx]

    return numpy.transpose(eigenVectors)

def scramble (data, secret):
    data_copied = data[:] 
    numpy.random.seed(secret)
    numpy.random.shuffle(data_copied)
    return data_copied

def unscramble(scrambled_data, secret, length = 64):
    numpy.random.seed(secret)
    order = range(length)
    numpy.random.shuffle(order)
    data = numpy.zeros(length)

    for i in range(length):
        data[order[i]] = scrambled_data[i]

    return data
