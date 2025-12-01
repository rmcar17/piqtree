from cogent3 import load_aligned_seqs

from piqtree import build_tree

import time

print("Loading alignment")
aln = load_aligned_seqs("aln_200_6000.fasta", moltype="dna")


print(len(aln.names), len(aln))

print("Loaded alignment")

print("Starting Python Build Tree")

start = time.time()
tree = build_tree(aln, "GTR+G", rand_seed=42)
finish = time.time()
print("FINISHED Python Build Tree")
print(f"Time taken: {finish - start:.2f} seconds")
