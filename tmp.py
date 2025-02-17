import os
import sys

# Add the directory containing the DLLs to the PATH
dll_path = os.path.join(os.path.dirname(__file__), 'C:/Users/rmcar/Documents/Projects/Python/piqtree/src/piqtree/_libiqtree')
os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']

import _piqtree