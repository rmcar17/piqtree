#include "bridge.h"
#include <string>

using namespace std;
// #include "libiqtree2_fun.h"

extern "C" int robinson_fould(const string& tree1, const string& tree2);

int my_c_robinson_fould(const char* tree1, const char* tree2) {
  // Call the function from your MinGW library
  return robinson_fould(tree1, tree2);
}