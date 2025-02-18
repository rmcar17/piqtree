#include "bridge.h"

extern "C" int bridge_rf(string& tree1, string& tree2);
extern "C" int robinson_fould(const string& tree1, const string& tree2);

int main() {
  string x = "(a,b,(c,(d,e)));";
  string y = "(a,b,(e,(d,c)));";
  string z = "(e,b,(c,(d,a)));";
  cout << bridge_rf(x, y) + bridge_rf(x, z) << endl;
  cout << robinson_fould(x, y) << endl;
  cout << robinson_fould(x, z) << endl;
  return 0;
}