
import numpy

import plotly
import plotly.plotly as py
import plotly.graph_objs as go

def write(P, Q, R, data, strength, min_vertices, cnt, k = 100):

    S = numpy.add(P**2, numpy.add(Q**2, R**2))

    #percentile = numpy.percentile(S, strength)

    if len(P) < min_vertices:
        return P, Q, R, 0

    start = int((100 - strength) * len(P)/100.0)

    count = 0

    # Create a trace
    trace = go.Scatter(
        x = range(len(P)),
        y = S
    )

    #data = [trace]

    #plotly.tools.set_credentials_file(username='aprieels', api_key='WyJUCfl1tdUNK7rLi1nN')

    #py.plot(data, filename='test' + str(cnt))
    
    for i in range(start, len(P)):

        #print P[i], Q[i], R[i]

        #if S[i] < percentile :
        minimum, intermediate, maximum = sorted([[P[i], 0], [Q[i], 1], [R[i], 2]], key=getKey)

        C_min = minimum[0]
        min_index = minimum[1]

        C_inter = intermediate[0]
        inter_index = intermediate[1]

        C_max = maximum[0]
        max_index = maximum[1]

        if inter_index != 2 :
        
            Mean = C_min + (C_max - C_min)/2

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

            #print P[i], Q[i], R[i]

            count += 1

    return P, Q, R, count

def getKey(item):
    return item[0]
