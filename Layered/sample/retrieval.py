
import numpy

def read(P, Q, R, strength):

    # Compute the maximum frequency from which we should read data
    S = numpy.add(P**2, numpy.add(Q**2, R**2))
    percentile = numpy.percentile(S, strength)

    data = []
    
    for i in range(0, len(P)):

        if S[i] >= percentile: #This frequency should not be considered, add 0.5 to the list of data so it doesn't have an impact on the retrieved data but the order remains correct
            data.append(0.5)
        else : #This frequency contains a bit that should be read

            C_min, C_inter, C_max = sorted([P[i], Q[i], R[i]])

            if C_inter != R[i] : 
            
                Mean = 0.5*C_max + 0.5*C_min

                # We use 4 intervals, so we want to know in which half C_inter is located
                if C_inter < Mean :
                    Min = C_min
                    Max = Mean
                else:
                    Min = Mean
                    Max = C_max

                Mean = (Min + Max)/2

                # Read the data bit
                if C_inter >= Mean:
                    data.append(1)
                else:
                    data.append(0)
            
            else:
                #We didn't insert a bit here because C_inter corresponds to the z-axis and we don't want to modify those coordinates
                data.append(0.5)

    return data