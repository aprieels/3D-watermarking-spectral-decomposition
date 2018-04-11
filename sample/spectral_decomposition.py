import numpy
import pymesh
import embedding
import retrieval
import partitioning
import random

def insert(filename_in, filename_out = 'out.obj', data = 32*[0, 1], secret = 123456, i0 = 0):

    scrambled_data = scramble(data, secret)

    mesh = pymesh.load_mesh(filename_in)

    patches = partitioning.layers_partitioning(mesh.faces, mesh.vertices, 10) #mesh_partitioning(filename_in, mesh.faces, mesh.num_vertices/500)

    updated_vertices = []

    for patch in patches:

        inside_vertices, inside_faces, indexes_mapping = remove_border_vertices(patch)

        if len(inside_vertices) > 0:
            B = compute_laplacian_matrix(len(inside_vertices), inside_faces)

            P = numpy.matmul(B, inside_vertices[:, 0])
            Q = numpy.matmul(B, inside_vertices[:, 1])
            R = numpy.matmul(B, inside_vertices[:, 2])

            P, Q, R = embedding.write(P, Q, R, data=scrambled_data, i0=i0)

            BM1 = numpy.linalg.inv(B)


            watermarked_vertices = numpy.zeros((len(inside_vertices), 3))

            watermarked_vertices[:, 0] = numpy.matmul(BM1, P)
            watermarked_vertices[:, 1] = numpy.matmul(BM1, Q)
            watermarked_vertices[:, 2] = inside_vertices[:, 2]

        new_vertices = numpy.zeros((patch.num_vertices, 3))

        for i in range(patch.num_vertices):
            if indexes_mapping[i] != 0:
                new_vertices[i] = watermarked_vertices[indexes_mapping[i] - 1]
            else:
                new_vertices[i] = patch.vertices[i]
            
        updated_vertices.append(pymesh.form_mesh(new_vertices, patch.faces))

    resulting_mesh = pymesh.merge_meshes(updated_vertices) # vertices_mean(updated_vertices, mesh.num_vertices)

    pymesh.save_mesh(filename_out, resulting_mesh)
    
def extract(filename, secret = 123456, length = 64, i0=0):

    mesh = pymesh.load_mesh(filename)

    patches = partitioning.layers_partitioning(mesh.faces, mesh.vertices, 10) #mesh_partitioning(filename_in, mesh.faces, mesh.num_vertices/500)

    print 'patched'

    data = []

    for patch in patches:

        inside_vertices, inside_faces, _ = remove_border_vertices(patch)
        
        if len(inside_vertices):
            B = compute_laplacian_matrix(len(inside_vertices), inside_faces)

            P = numpy.matmul(B, inside_vertices[:, 0])
            Q = numpy.matmul(B, inside_vertices[:, 1])
            R = numpy.matmul(B, inside_vertices[:, 2])

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

def remove_border_vertices(patch):
    vertices = patch.vertices
    faces = patch.faces

    is_on_border = numpy.zeros(patch.num_vertices, dtype=bool)
    indexes_mapping = numpy.zeros(patch.num_vertices, dtype=int)
    
    inside_vertices = []
    inside_faces = []

    max_z = numpy.max(vertices[:, 2])
    min_z = numpy.min(vertices[:, 2])

    for i, vertice in enumerate(vertices):
        if vertice[2] == max_z or vertice[2] == min_z:
            is_on_border[i] = True

    for face in faces:
        if not is_on_border[face[0]] and not is_on_border[face[1]] and not is_on_border[face[2]]:
            for i in range(3):
                if (indexes_mapping[face[i]] == 0) :
                    inside_vertices.append(vertices[face[i]])
                    indexes_mapping[face[i]] = len(inside_vertices)
            inside_faces.append([indexes_mapping[face[0]] - 1, indexes_mapping[face[1]] - 1, indexes_mapping[face[2]] - 1])

    return numpy.array(inside_vertices), numpy.array(inside_faces), indexes_mapping