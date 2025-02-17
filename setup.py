"""setup for piqtree."""

import os
import platform
import subprocess
from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

# Function to find all DLLs in a directory
def find_dlls(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.dll')]

DLL_PATH = "C:/Users/rmcar/Documents/Projects/Python/piqtree/src/piqtree/_libiqtree"
dlls = find_dlls(DLL_PATH)

LIBRARY_DIR = "src/piqtree/_libiqtree"


def get_brew_prefix(package: str) -> Path:
    """Get the prefix path for a specific Homebrew package."""
    return Path(
        subprocess.check_output(["brew", "--prefix", package]).strip().decode("utf-8"),
    )


if platform.system() == "Darwin":
    brew_prefix_llvm = get_brew_prefix("llvm")
    brew_prefix_libomp = get_brew_prefix("libomp")

    # Use Homebrew's clang/clang++
    os.environ["CC"] = str(brew_prefix_llvm / "bin" / "clang")
    os.environ["CXX"] = str(brew_prefix_llvm / "bin" / "clang++")

    # Define OpenMP flags and libraries for macOS
    openmp_flags = ["-Xpreprocessor", "-fopenmp"]
    openmp_libs = ["omp"]

    # Use the paths from Homebrew for libomp
    openmp_include = str(brew_prefix_libomp / "include")
    library_dirs = [
        str(brew_prefix_libomp / "lib"),
        str(brew_prefix_llvm / "lib"),
    ]
else:
    openmp_flags = ["-fopenmp"]
    openmp_libs = ["gomp"]
    openmp_include = None
    library_dirs = []

# ext_modules = [
#     Pybind11Extension(
#         "_piqtree",
#         ["src/piqtree/_libiqtree/_piqtree.cpp"],
#         library_dirs=[
#             *library_dirs,
#             LIBRARY_DIR,
#         ],
#         libraries=["iqtree2", "z", *openmp_libs],
#         extra_compile_args=openmp_flags,
#         include_dirs=[openmp_include] if openmp_include else [],
#     ),
# ]

ext_modules = [
    Pybind11Extension(
        "_piqtree",
        ["src/piqtree/_libiqtree/_piqtree.cpp"],
        library_dirs=[
            # *library_dirs,
            # LIBRARY_DIR,
            "C:/Users/rmcar/Documents/Projects/Python/piqtree/src/piqtree/_libiqtree"
        ],
        # libraries=["iqtree2", "z", *openmp_libs],
        libraries=["bridge"],
        # extra_compile_args=["-std=c++11"],
        # extra_link_args=[f"-L{LIBRARY_DIR}", "-lbridge"],
        # include_dirs=[openmp_include] if openmp_include else [],
        package_data={
        '': ['*.dll'],
        },
        data_files=[(DLL_PATH, dlls)]
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
