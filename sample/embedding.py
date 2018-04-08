
import numpy

def write(P, Q, R, data, i0, k = 100):

    S = numpy.add(P**2, numpy.add(Q**2, R**2))

    percentile = numpy.percentile(S, i0)

    count = 0
    
    for i in range(0, len(P)):

        if S[i] < percentile :
            minimum, intermediate, maximum = sorted([[P[i], 0], [Q[i], 1], [R[i], 2]], key=getKey)

            C_min = minimum[0]
            min_index = minimum[1]

            C_inter = intermediate[0]
            inter_index = intermediate[1]

            C_max = maximum[0]
            max_index = maximum[1]
            
            Mean = C_min + (C_max - C_min)/2

            if data[count%len(data)]:
                if C_inter < Mean:
                    if inter_index == 2:
                        C_min = C_min - (Mean - C_inter)/k
                        C_max = C_max - (Mean - C_inter)/k #On ne peut pas modifier C_inter donc on modifie la moyenne
                    else:
                        C_inter = Mean + (Mean - C_inter)/k 
            else:
                if C_inter > Mean:
                    if inter_index == 2:
                        C_min = C_min + (C_inter - Mean)/k
                        C_max = C_max + (C_inter - Mean)/k
                        '''Mean = C_inter + (Mean - C_inter)/k
                        C_min = (2*Mean - C_max)'''
                    else:
                        C_inter = Mean - (C_inter - Mean)/k 

            values = numpy.zeros(3)
            values[min_index] = C_min
            values[inter_index] = C_inter
            values[max_index] = C_max

            [P[i], Q[i], R[i]] = values

            count += 1

    return P, Q, R

def getKey(item):
    return item[0]

'''

C_inter = Mean + (Mean - C_inter)/k 

Mean = C_inter - (Mean - C_inter)/k
C_max = (Mean - C_min)*2 + C_min

'''