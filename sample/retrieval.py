
import numpy

def read(P, Q, R, i0):

    S = numpy.add(P**2, numpy.add(Q**2, R**2))

    percentile = numpy.percentile(S, i0)

    data = []
    count = 0

    for i in range(0, len(P)):

        if S[i] < percentile :

            C_min, C_inter, C_max = sorted([P[i], Q[i], R[i]])
            
            Mean = C_max - (C_max - C_min)/2

            if C_inter >= Mean:
                data.append(1)
            else:
                data.append(0)

            count += 1

    print data

    return data