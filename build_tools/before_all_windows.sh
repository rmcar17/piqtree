choco install -y boost-msvc-14.1 
choco install -y llvm --version=14.0.6
choco install -y eigen
choco install -y make

bash build_tools/build_iqtree.sh