# Setup for Windows

`cmake -G "MinGW Makefiles" -DBUILD_LIB=ON -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ ..`
`cmake -G "MinGW Makefiles" -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_MAKE_PROGRAM=make -DCMAKE_C_FLAGS="-IC:/ProgramData/chocolatey/lib/eigen/include/eigen3 --target=x86_64-pc-windows-gnu" -DCMAKE_CXX_FLAGS="-IC:/ProgramData/chocolatey/lib/eigen/include/eigen3 --target=x86_64-pc-windows-gnu" -DBUILD_LIB=ON ..`


`gcc -shared -o bridge.dll bridge.cpp -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2/main -LC:/Users/rmcar/Documents/Projects/Python/piqtree/tmp`
`clang -shared -o bridge.dll bridge.cpp -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2/main -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2 -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2/build -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2/yaml-cpp/include -LC:/Users/rmcar/Documents/Projects/Python/piqtree/tmp`



`g++ -shared -o bridge.dll bridge.cpp -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2/main -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2 -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2/build -IC:/Users/rmcar/Documents/Projects/Python/piqtree/iqtree2/yaml-cpp/include -LC:/Users/rmcar/Documents/Projects/Python/piqtree/tmp`