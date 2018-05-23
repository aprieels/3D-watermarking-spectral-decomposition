
import numpy

def read(P, Q, R, i0):

    S = numpy.add(P**2, numpy.add(Q**2, R**2))

    percentile = numpy.percentile(S, i0)

    data = []
    
    for i in range(0, len(P)):

        if S[i] >= percentile:
            data.append(0.5)
        else :

            C_min, C_inter, C_max = sorted([P[i], Q[i], R[i]])
            
            Mean = 0.5*C_max + 0.5*C_min

            if C_inter < Mean :
                Min = C_min
                Max = Mean
            else:
                Min = Mean
                Max = C_max

            Mean = (Min + Max)/2

            if C_inter >= Mean:
                data.append(1)
            else:
                data.append(0)

    return data