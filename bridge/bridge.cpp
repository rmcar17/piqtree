#include "bridge.h"

int main() {
  string tree1 = "(a,b,(c,(d,e)));";
  string tree2 = "(e,b,(c,(d,a)));";

  cout << bridge_rf(tree1, tree2) << endl;
  return 0;
}