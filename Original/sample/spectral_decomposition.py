import numpy as np
import pymesh
import sys
import os
import random

import embedding
import retrieval
import partitioning
import utils

'''
    Inserts the content of @data inside @filename_in and saves it as @filename_out, the data is scramble with the key @secret, a @strength of a number of patches @partitions
'''
def insert(filename_in, filename_out = 'out.obj', data = 32*[0, 1], secret = 123456, strength = 100, partitions = -1):

    print
    print '########## Embedding started ##########'

    # Scramble the data
    scrambled_data = scramble(data, secret)

    mesh = pymesh.load_mesh(filename_in)

    if partitions == -1:
        partitions = mesh.num_vertices/500

    # Partition the mesh into patches
    patches, mapping = partitioning.mesh_partitioning(filename_in, mesh, partitions)

    print 'Step 1: Mesh patched'

    processed = 0
    bits_inserted = 0
    updated_vertices = []

    # Set a progress bar
    utils.progress(processed, len(patches), 'Inserting data in patches...')

    # Insert the data in all the patches
    for i, patch in enumerate(patches):

        # Get the eigenVectors, either by computing them or by reading the from a file if they already have been computed
        npy_file = 'saved_eig/' + str(partitions) + '/embedding_' + str(i) + '.npy'

        if os.path.exists(npy_file) :
            B = np.load(npy_file)
        else :
            B = compute_eigenvectors(patch.num_vertices, patch.faces)
            np.save(npy_file, B)

        # Get the spectral coefficients
        P = np.matmul(B, patch.vertices[:, 0])
        Q = np.matmul(B, patch.vertices[:, 1])
        R = np.matmul(B, patch.vertices[:, 2])

        # Insert the data
        P, Q, R, count = embedding.write(P, Q, R, scrambled_data, strength)

        BM1 = np.linalg.pinv(B)

        new_vertices = np.zeros((patch.num_vertices, 3))

        # Retrieve the new coordinates of the vertices
        new_vertices[:, 0] = np.matmul(BM1, P)
        new_vertices[:, 1] = np.matmul(BM1, Q)
        new_vertices[:, 2] = np.matmul(BM1, R)
        
        updated_vertices.append(pymesh.form_mesh(new_vertices, patch.faces))

        bits_inserted += count

        # Update the progress bar
        processed += 1
        utils.progress(processed, len(patches), 'Inserting data in patches...')

    print
    print 'Step 2: Data inserted'

    if bits_inserted < len(data):
        print 'Only %s bits inserted, the bit error rate when retriving data might be significant' % (bits_inserted)

    new_vertices = np.zeros((mesh.num_vertices, 3))

    # Merge the different patches into a single mesh
    for i in range(mesh.num_vertices):
        for j in range(partitions):
            val = mapping[j][i]
            if val != -1:
                new_vertices[i] = updated_vertices[j].vertices[int(val)]
                continue
        
    pymesh.save_mesh(filename_out, pymesh.form_mesh(new_vertices, mesh.faces))

    print '########## Embedding finished ##########'
    print

    return bits_inserted

'''
    Extracts the data (of @length) that has been scrambled with @secret, contained in the mesh saved as @filename that has been inserted using a number of patches @partitions
'''    
def extract(filename, secret = 123456, length = 64, strength=100, partitions = -1):

    print
    print '########## Retrieval started ##########'

    mesh = pymesh.load_mesh(filename)

    if partitions == -1:
        partitions = mesh.num_vertices/500

    # Partition the watermarked mesh into patches
    patches, _ = partitioning.mesh_partitioning(filename, mesh, partitions)

    print 'Step 1: Mesh patched'

    data = []

    processed = 0
    utils.progress(processed, len(patches), 'Reading data from patches...')

    # Extract the data from all the patches
    for i, patch in enumerate(patches):

        # Get the eigenVectors, either by computing them or by reading the from a file if they already have been computed
        npy_file = 'saved_eig/' + str(partitions) + '/retrieval_' + str(i) + '.npy'

        if os.path.exists(npy_file) :
            B = np.load(npy_file)
        else :
            B = compute_eigenvectors(patch.num_vertices, patch.faces)
            np.save(npy_file, B)

        # Get the spectral coefficients
        P = np.matmul(B, patch.vertices[:, 0])
        Q = np.matmul(B, patch.vertices[:, 1])
        R = np.matmul(B, patch.vertices[:, 2])

        # Read the data and add it to the list of data retrieved
        data.append(retrieval.read(P, Q, R, strength))

        # Update the progress bar
        processed += 1
        utils.progress(processed, len(patches), 'Reading data from patches...')

    print
    print 'Step 2: Data retrieved'

    # Use a majority vote to get the data then unscramble it
    final_data = unscramble(data_majority(data, length), secret)

    print '########## Retrieval finished ##########'
    print

    return final_data

'''
    Transforms the redundancy it a single data array of @length using a majority
'''
def data_majority(data, length):
    final_data = np.zeros(length)

    for i in range(length):
        sum = 0.0
        count = 0

        #Go through each possible data
        for d in data:
            j = i

            #Find all occurences of this specific bit
            while j < len(d):
                sum += d[j]
                count += 1
                j += length

        # Decide what bit we should read based on the majority
        if count > 0:
            final_data[i] = round(sum/count)

    return final_data


'''
    Computes the eigenvectors of the mesh represented in @patch
'''
def compute_eigenvectors (num_vertices, patch):

    laplacian = np.zeros((num_vertices, num_vertices))

    # Get the list of neighbors and the valence of each vertice
    star, d = utils.get_neighbors_and_valence(num_vertices, patch)

    # Compute the Laplacian
    for i in range(num_vertices):
        laplacian[i][i] = 1
        for j in star[i]:
            laplacian[i][int(j)] = -1.0/d[i]
            
    # Get the eigenvectors and eigenvalues of the laplacian
    eigenValues, eigenVectors = np.linalg.eig(laplacian)

    # Sort the eigenvectors regarding to their eigenvalues
    idx = eigenValues.argsort()
    eigenValues = eigenValues[idx]
    eigenVectors = eigenVectors[:,idx]

    return np.transpose(eigenVectors)

'''
    Scramble @data with the key @secret
'''
def scramble (data, secret):
    data_copied = data[:] 
    np.random.seed(secret)
    np.random.shuffle(data_copied)
    return data_copied

'''
    Unscramble @scrambled_data with the key @secret and that has a length of @length
'''
def unscramble(scrambled_data, secret, length = 64):
    np.random.seed(secret)
    order = range(length)
    np.random.shuffle(order)
    data = np.zeros(length)

    for i in range(length):
        data[order[i]] = scrambled_data[i]

    return data
