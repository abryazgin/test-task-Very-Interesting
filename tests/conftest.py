import os
import sys

# adding `src` dir to PYTHON_PATH for importing modules
rootdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(rootdir, 'src'))
