import random
import os
import sys
import pymesh
import numpy
import time

from context import partitioning
from context import spectral_decomposition
from context import distortion
from context import attacks

def insert_extract(filename_in = os.path.join(os.path.dirname(__file__), 'source_models/bunny_new.ply'), data = [random.randrange(2) for _ in range(64)], filename_out = os.path.join(os.path.dirname(__file__), 'watermarked_models/out.obj'), secret=123456, i0 = 10, partitions = -1):

    print 'Data to be inserted: ', data
    
    start = time.time()
    spectral_decomposition.insert(filename_in, filename_out, data, secret, i0, partitions)
    middle = time.time()
    data_retrieved = spectral_decomposition.extract(filename_out, secret, 64, i0, partitions)
    end = time.time()

    n_errors = len([x for x, y in zip(data, data_retrieved) if x != y])

    print 'Data retrieved: ', data_retrieved
    print 'Number of errors: ', n_errors
    print 'Time embedding: ', middle - start
    print 'Time retrieval: ', end - middle

    return n_errors

def test_partitions():
    m = pymesh.load_mesh(os.path.join(os.path.dirname(__file__), './source_models/bunny_new.stl'))
    patches, _ = partitioning.mesh_partitioning('./source_models/bunny.stl', m, 2) 

    for i, patch in enumerate(patches):
        pymesh.save_mesh('test_partitions_'+str(i)+'.stl', patch)

def generate_sample():
    data = [0, 1]*32
    write_file = "test_data/original_spectral.csv"

    with open(write_file, 'a+') as output:

        lines_count = len(output.readlines())
        count = 0

        for patches in range(100, 10, -10) :
            for strength in [1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100]:
                if count < lines_count:
                    count += 1 
                    continue

                print ''
                print 'Starting strength = %d, patches = %d' % (strength, patches)
                print ''

                out_name = "watermarked_models/generated/bunny_strength"+str(strength)+ "_patches" + str(patches) + ".obj"

                start = time.time()
                capacity = spectral_decomposition.insert("source_models/bunny_new.stl", out_name, data, 123456, strength, patches, 2)
                middle = time.time()
                if capacity >= 0 : 
                    retrieved = spectral_decomposition.extract(out_name, 123456, 64, strength, patches)
                end = time.time()

                n_errors = len([x for x, y in zip(data, retrieved) if x != y])

                print n_errors

                original_mesh = pymesh.load_mesh("source_models/bunny_new.stl")
                watermarked_mesh = pymesh.load_mesh(out_name)

                print 'Embedded and retrieved'
                print ''

                rms = distortion.rms_error(original_mesh, watermarked_mesh)
                print 'RMS Error Computed'
                hausdorff = distortion.hausdorff_distance(original_mesh, watermarked_mesh)
                print 'Hausdorff Distance Computed'
                smoothness = distortion.local_smoothness(original_mesh, watermarked_mesh)
                print 'Local Smoothness Computed'

                print ''
                print 'Done strength = %d, patches = %d' % (strength, patches)
                print ''

                output.write(str(strength) + ", " + str(patches) + ", " + str(capacity) + ", " + str(middle-start) + ', ' + str(end-middle) + ', ' + str(n_errors) + ', ' + str(rms) + ', ' + str(hausdorff) + ', ' + str(smoothness) +";\n")

                output.flush()

    output.close()

def test_attacks():
    
    data = [0, 1]*32
    write_file = "test_data/original_spectral_attacks.csv"

    with open(write_file, 'a+') as output:

        patches = 60

        for strength in [1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100]:  

            file_name = "watermarked_models/generated/bunny_strength"+str(strength)+ "_patches" + str(patches) + ".obj"
            data = [0, 1]*32
            watermarked_mesh = pymesh.load_mesh(file_name) 
            
            for iterations in [1, 2, 3, 5, 7, 10]:
                file_smoothed = "watermarked_models/generated/smoothed/bunny_strength"+str(strength)+ "_patches" + str(patches) + "_iterations" + str(iterations) + ".obj"
                pymesh.save_mesh(file_smoothed, attacks.smoothing(watermarked_mesh, iterations))
                retrieved = spectral_decomposition.extract(file_smoothed, 123456, 64, strength, patches)
                n_errors = len([x for x, y in zip(data, retrieved) if x != y])
                output.write("SMOOTHING, " + str(strength) + ", " + str(patches) + ", " + str(iterations) + "," + str(n_errors) + ";\n")
                output.flush()

            for amplitude in [0.01, 0.02, 0.03, 0.05, 0.07, 0.1]:
                file_noisy = "watermarked_models/generated/noisy/bunny_strength"+str(strength)+ "_patches" + str(patches) + "_amplitude" + str(amplitude) + ".obj"
                pymesh.save_mesh(file_noisy, attacks.noise(watermarked_mesh, amplitude))
                retrieved = spectral_decomposition.extract(file_noisy, 123456, 64, strength, patches)
                n_errors = len([x for x, y in zip(data, retrieved) if x != y])
                output.write("NOISE, " + str(strength) + ", " + str(patches) + ", " + str(amplitude) + ", " + str(n_errors) + ";\n")
                output.flush()


if __name__ == '__main__':
    generate_sample()