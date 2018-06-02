
import numpy

def write(P, Q, R, data, i0, k = 100):

    S = numpy.add(P**2, numpy.add(Q**2, R**2))

    percentile = numpy.percentile(S, i0)

    count = 0
    inserted = 0

    for i in range(0, len(P)):

        if S[i] >= percentile:
            count += 1
        
        else :

            minimum, intermediate, maximum = sorted([[P[i], 0], [Q[i], 1], [R[i], 2]], key=get_key)
        
            C_min = minimum[0]
            min_index = minimum[1]

            C_inter = intermediate[0]
            inter_index = intermediate[1]

            C_max = maximum[0]
            max_index = maximum[1]

            if inter_index != 2 :
            
                Mean = 0.5*C_max + 0.5*C_min

                if C_inter < Mean :
                    Min = C_min
                    Max = Mean
                else:
                    Min = Mean
                    Max = C_max

                Mean = (Min + Max)/2

                if data[count%len(data)]:
                    if C_inter < Mean :
                        C_inter = Mean + (Mean - C_inter)/k 
                else:
                    if C_inter > Mean :
                        C_inter = Mean - (C_inter - Mean)/k 

                values = numpy.zeros(3)
                values[min_index] = C_min
                values[inter_index] = C_inter
                values[max_index] = C_max                    

                [P[i], Q[i], R[i]] = values
                inserted += 1

            count += 1

    return P, Q, R, inserted

def get_key(item):
    return item[0]
