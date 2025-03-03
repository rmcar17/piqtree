#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

namespace py = pybind11;

extern "C" int bridge_rf(string& tree1, string& tree2);


PYBIND11_MODULE(_piqtree, m) {
  m.doc() = "piqtree - Unlock the Power of IQ-TREE 2 with Python!";

  m.def("bridge_rf", &bridge_rf);
}
