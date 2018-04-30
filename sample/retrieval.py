
import numpy

def read(P, Q, R, strength, min_vertices):

    S = numpy.add(P**2, numpy.add(Q**2, R**2))

    #percentile = numpy.percentile(S, strength)

    if len(P) < min_vertices:
        return []

    start = int((100 - strength) * len(P)/100.0)

    data = []
    count = 0

    for i in range(start, len(P)):

        #if S[i] < percentile :

        C_min, C_inter, C_max = sorted([P[i], Q[i], R[i]])

        if C_inter != R[i] :
        
            Mean = C_max - (C_max - C_min)/2

            if C_inter >= Mean:
                data.append(1)
            else:
                data.append(0)

            count += 1

    return data