#include "bridge.h"
#include "c_libiqtree2.h"

int my_c_robinson_fould(const char* tree1, const char* tree2) {
  // Call the function from your MinGW library
  return c_robinson_fould(tree1, tree2);
}