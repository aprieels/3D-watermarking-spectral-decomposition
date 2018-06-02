import sys
import numpy

'''
    Set a progress bar, with a @total and a current value of @count
'''
def progress(count, total, prefix=''):
    bar_length = 50
    filled_len = int(round(bar_length * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_length - filled_len)

    sys.stdout.write('%s [%s] %s%s | %s/%s\r' % (prefix, bar, percents, '%', count, total))
    sys.stdout.flush()

def get_neighbors_and_valence(num_vertices, faces):
    star = []
    for i in range(num_vertices):
        star.append([])

    d = numpy.zeros(num_vertices)

    for face in faces: 
        for i in range(3):
            if star[face[i]] == None:
                star[face[i]] = []
            for j in range(3):
                if i != j:
                    if face[j] not in star[face[i]]:
                        star[face[i]].append(face[j])
                        d[face[i]] += 1

    return star, d