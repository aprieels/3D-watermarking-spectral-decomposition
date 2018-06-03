import numpy as np
import pymesh
import sys
import os
import random

import embedding
import retrieval
import partitioning
import orientation
import utils
import distortion

'''
    Inserts the content of @data inside @filename_in and saves it as @filename_out, the data is scramble with the key @secret, a @strength of a number of patches @partitions, all the patches that have a visual distancce greater than @visual_distance are not considered
'''
def insert(filename_in, filename_out = 'out.obj', data = 32*[0, 1], axis = [0, 0, 1], secret = 123456, strength = 100, partitions = -1, visual_distance = sys.maxint):

    print
    print '########## Embedding started ##########'

    # Scramble the data
    scrambled_data = scramble(data, secret)

    mesh = pymesh.load_mesh(filename_in)

    # Orient the mesh
    vertices = orientation.orient_mesh(mesh.vertices, axis)

    if partitions == -1:
        partitions = mesh.num_vertices/500

    print 'Step 1: Mesh oriented'

    # Partition the mesh into layers
    patches = partitioning.layers_partitioning(mesh.faces, vertices, partitions)

    print 'Step 2: Mesh patched'

    processed = 0
    bits_inserted = 0
    updated_vertices = []

    # Set a progress bar
    utils.progress(processed, len(patches), 'Inserting data in patches...')

    # Insert the data in all the layers
    for i, patch in enumerate(patches):

        # Remove the vertices on the border of the mesh to avoid discontinuities
        inside_vertices, inside_faces, indexes_mapping = remove_border_vertices(patch)

        if len(inside_vertices) > 0:

            # Get the eigenVectors, either by computing them or by reading the from a file if they already have been computed
            npy_file = 'saved_eig/' + str(partitions) + '/embedding_' + str(i) + '.npy'

            if os.path.exists(npy_file) :
                B = np.load(npy_file)
            else :
                B = compute_eigenvectors(len(inside_vertices), inside_faces)
                np.save(npy_file, B)

            # Get the spectral coefficients
            P = np.matmul(B, inside_vertices[:, 0])
            Q = np.matmul(B, inside_vertices[:, 1])
            R = np.matmul(B, inside_vertices[:, 2])

            # Insert the data
            P, Q, R, count = embedding.write(P, Q, R, scrambled_data, strength)

            BM1 = np.linalg.pinv(B)

            watermarked_vertices = np.zeros((len(inside_vertices), 3))

            # Retrieve the new coordinates of the vertices
            watermarked_vertices[:, 0] = np.matmul(BM1, P)
            watermarked_vertices[:, 1] = np.matmul(BM1, Q)
            watermarked_vertices[:, 2] = np.matmul(BM1, R)

            # Compute the Hausdorff Distance
            distance = distortion.hausdorff_distance(pymesh.form_mesh(inside_vertices, inside_faces), pymesh.form_mesh(watermarked_vertices, inside_faces))

            # Restore the vertices if the layer is too much deformed
            if distance > visual_distance :
                print ''
                print 'Too much distortions, patch discarded ', distance
                watermarked_vertices = inside_vertices
            else :
                bits_inserted += count

        new_vertices = np.zeros((patch.num_vertices, 3))

        # Merge the watermarked vertices with the vertices on the border of the layer that were discarded
        for i in range(patch.num_vertices):
            if indexes_mapping[i] != 0:
                new_vertices[i] = watermarked_vertices[indexes_mapping[i] - 1]
            else:
                new_vertices[i] = patch.vertices[i]
        
        updated_vertices.append(pymesh.form_mesh(new_vertices, patch.faces))

        # Update the progress bar
        processed += 1
        utils.progress(processed, len(patches), 'Inserting data in patches...')

    print
    print 'Step 3: Data inserted'

    if bits_inserted < len(data):
        print 'Only %s bits inserted, the bit error rate when retriving data might be significant' % (bits_inserted)
        
    # Merge the different layers into a single mesh
    resulting_mesh = partitioning.merge(updated_vertices)

    pymesh.save_mesh(filename_out, resulting_mesh)

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

    # Partition the watermarked mesh into layers
    patches = partitioning.layers_partitioning(mesh.faces, mesh.vertices, partitions)

    print 'Step 1: Mesh patched'

    data = []

    processed = 0
    utils.progress(processed, len(patches), 'Reading data from patches...')

    # Extract the data from all the patches
    for i, patch in enumerate(patches):

        # Remove the vertices on the border of the mesh that were not considered during the insertion
        inside_vertices, inside_faces, _ = remove_border_vertices(patch)
        
        if len(inside_vertices):
            
            # Get the eigenVectors, either by computing them or by reading the from a file if they already have been computed
            npy_file = 'saved_eig/' + str(partitions) + '/retrieval_' + str(i) + '.npy'

            if os.path.isfile(npy_file) :
                B = np.load(npy_file)
            else :
                B = compute_eigenvectors(len(inside_vertices), inside_faces)
                np.save(npy_file, B)

            # Get the spectral coefficients
            P = np.matmul(B, inside_vertices[:, 0])
            Q = np.matmul(B, inside_vertices[:, 1])
            R = np.matmul(B, inside_vertices[:, 2])

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

'''
    Remove the faces on the border of a layer from the maximum and minimum z values
'''
def remove_border_vertices(patch):
    vertices = patch.vertices
    faces = patch.faces

    is_on_border = np.zeros(patch.num_vertices, dtype=bool)
    indexes_mapping = np.zeros(patch.num_vertices, dtype=int)
    
    inside_vertices = []
    inside_faces = []

    # Get the maximum and minimum z values
    max_z = np.max(vertices[:, 2])
    min_z = np.min(vertices[:, 2])

    # Mark all the vertices located on the border of a layer
    for i, vertice in enumerate(vertices):
        if vertice[2] == max_z or vertice[2] == min_z:
            is_on_border[i] = True

    # Remove the faces that have a vertice on the border of the layer
    for face in faces:
        if not is_on_border[face[0]] and not is_on_border[face[1]] and not is_on_border[face[2]]:
            for i in range(3):
                if (indexes_mapping[face[i]] == 0) :
                    inside_vertices.append(vertices[face[i]])
                    indexes_mapping[face[i]] = len(inside_vertices)
            inside_faces.append([indexes_mapping[face[0]] - 1, indexes_mapping[face[1]] - 1, indexes_mapping[face[2]] - 1])

    return np.array(inside_vertices), np.array(inside_faces), indexes_mapping