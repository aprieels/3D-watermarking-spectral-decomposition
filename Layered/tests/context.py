import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sample')))

# Facilitates the import of the modules into the tests

# pylint: disable=import-error
import embedding
import orientation
import partitioning
import retrieval
import spectral_decomposition
import distortion
import attacks
