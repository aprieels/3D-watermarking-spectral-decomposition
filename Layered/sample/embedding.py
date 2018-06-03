
import numpy as np

'''
    Inserts the content of @data inside the spectrum of a mesh: @P, @Q, @R
'''
def write(P, Q, R, data, strength, k = 100):

    # Determine which frequencies to modify
    S = np.add(P**2, np.add(Q**2, R**2))
    percentile = np.percentile(S, strength)

    count = 0
    inserted = 0

    for i in range(0, len(P)):

        if S[i] >= percentile: #This frequency should not be modified
            count += 1
        
        else : #This frequency should be modified

            minimum, intermediate, maximum = sorted([[P[i], 0], [Q[i], 1], [R[i], 2]], key=get_key)
        
            # Order P, Q, R
            C_min = minimum[0]
            C_inter = intermediate[0]
            C_max = maximum[0]

            # Remember to which of P, Q and R corresponds C_min, C_inter and C_max
            min_index = minimum[1]
            inter_index = intermediate[1]
            max_index = maximum[1]
            
            if inter_index != 2 :
                Mean = 0.5*C_max + 0.5*C_min

                # We want to use 4 intervals
                if C_inter < Mean :
                    Min = C_min
                    Max = Mean
                else:
                    Min = Mean
                    Max = C_max

                Mean = (Min + Max)/2

                # Change C_inter from interval if needed
                if data[count%len(data)]:
                    if C_inter < Mean :
                        C_inter = Mean + (Mean - C_inter)/k 
                else:
                    if C_inter > Mean :
                        C_inter = Mean - (C_inter - Mean)/k 

                # Reassign P, Q and R to their new value
                values = np.zeros(3)
                values[min_index] = C_min
                values[inter_index] = C_inter
                values[max_index] = C_max                    

                [P[i], Q[i], R[i]] = values
                inserted += 1

            count += 1

    return P, Q, R, inserted

def get_key(item):
    return item[0]
