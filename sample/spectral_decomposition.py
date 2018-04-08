import numpy
import pymesh
import embedding
import retrieval
import partitioning
import random

def insert(filename_in, filename_out = 'out.obj', data = 32*[0, 1], secret = 123456, i0 = 0):

    scrambled_data = scramble(data, secret)

    mesh = pymesh.load_mesh(filename_in)

    patches = partitioning.layers_partitioning(mesh.faces, mesh.vertices, 20) #mesh_partitioning(filename_in, mesh.faces, mesh.num_vertices/500)

    updated_vertices = []

    for patch in patches:

        B = compute_laplacian_matrix(patch.num_vertices, patch.faces)

        P = numpy.matmul(B, patch.vertices[:, 0])
        Q = numpy.matmul(B, patch.vertices[:, 1])
        R = numpy.matmul(B, patch.vertices[:, 2])

        P, Q, R = embedding.write(P, Q, R, data=scrambled_data, i0=i0)

        BM1 = numpy.linalg.inv(B)

        new_vertices = numpy.zeros((patch.num_vertices, 3))

        new_vertices[:, 0] = numpy.matmul(BM1, P)
        new_vertices[:, 1] = numpy.matmul(BM1, Q)
        new_vertices[:, 2] = patch.vertices[:, 2]#numpy.matmul(BM1, R)

        updated_vertices.append(pymesh.form_mesh(new_vertices, patch.faces))

    resulting_mesh = pymesh.merge_meshes(updated_vertices) # vertices_mean(updated_vertices, mesh.num_vertices)

    pymesh.save_mesh(filename_out, resulting_mesh)
    
def extract(filename, secret = 123456, length = 64, i0=0):

    mesh = pymesh.load_mesh(filename)

    patches = partitioning.layers_partitioning(mesh.faces, mesh.vertices, 20) #mesh_partitioning(filename_in, mesh.faces, mesh.num_vertices/500)

    print 'patched'

    data = []

    for patch in patches:

        B = compute_laplacian_matrix(patch.num_vertices, patch.faces)

        P = numpy.matmul(B, patch.vertices[:, 0])
        Q = numpy.matmul(B, patch.vertices[:, 1])
        R = numpy.matmul(B, patch.vertices[:, 2])

        data.append(retrieval.read(P, Q, R, i0))

    final_data = unscramble(data_majority(data, length), secret)

    return final_data

def vertices_mean(updated_vertices, num_vertices):
    vertices = numpy.zeros((num_vertices, 3))
    for i in range(num_vertices):
        for j in range(3):
            total = 0.0
            count = 0.0
            for uv in updated_vertices:
                if uv[1][i] > 0:
                    total += uv[0][i][j]
                    count += 1
            vertices[i][j] = total/count
    return vertices
                

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
        final_data[i] = round(sum/count)
    return final_data

def compute_laplacian_matrix (num_vertices, patch):

    star = []
    for i in range(num_vertices):
        star.append([])

    d = numpy.zeros(num_vertices)
    laplacian = numpy.zeros((num_vertices, num_vertices))

    for face in patch: 
        for i in range(3):
            if star[face[i]] == None:
                star[face[i]] = []
            for j in range(3):
                if i != j:
                    if face[j] not in star[face[i]]:
                        star[face[i]].append(face[j])
                        d[face[i]] += 1

    for i in range(num_vertices):
        laplacian[i][i] = 1
        for j in star[i]:
            laplacian[i][int(j)] = -1.0/d[i]
            
    eigenValues, eigenVectors = numpy.linalg.eig(laplacian)

    idx = eigenValues.argsort()[::-1]   
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