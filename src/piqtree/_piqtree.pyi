"""_piqtree - Linking IQ-TREE to Python!"""

from collections.abc import Sequence
from typing import Annotated

import numpy
from numpy.typing import NDArray


__iqtree_version__: str = ...

def iq_robinson_fould(tree1: str, tree2: str) -> int:
    """Calculates the robinson fould distance between two trees"""

def iq_random_tree(num_taxa: int, tree_gen_mode: str, num_trees: int, rand_seed: int) -> str:
    """
    Generates a set of random phylogenetic trees. tree_gen_mode allows:"YULE_HARDING", "UNIFORM", "CATERPILLAR", "BALANCED", "BIRTH_DEATH", "STAR_TREE".
    """

def iq_build_tree(names: Sequence[str], seqs: Sequence[str], model: str, rand_seed: int, bootstrap_replicates: int, num_threads: int, other_options: str) -> str:
    """
    Perform phylogenetic analysis on the input alignment (in string format). With estimation of the best topology.
    """

def iq_fit_tree(names: Sequence[str], seqs: Sequence[str], model: str, tree: str, bl_fixed: bool, rand_seed: int, num_threads: int, other_options: str) -> str:
    """
    Perform phylogenetic analysis on the input alignment (in string format). With restriction to the input toplogy.
    """

def iq_model_finder(names: Sequence[str], seqs: Sequence[str], rand_seed: int, model_set: str, freq_set: str, rate_set: str, num_threads: int, other_options: str) -> str:
    """Find optimal model for an alignment."""

def iq_jc_distances(names: Sequence[str], seqs: Sequence[str], num_threads: int) -> Annotated[NDArray[numpy.float64], dict(shape=(None,))]:
    """Construct pairwise distance matrix for alignment."""

def iq_nj_tree(names: Sequence[str], distances: Annotated[NDArray[numpy.float64], dict(shape=(None,), order='C', device='cpu', writable=False)]) -> str:
    """Build neighbour-joining tree from distance matrix."""

def iq_consensus_tree(trees: Sequence[str], min_support: float) -> str:
    """Compute a consensus tree from a sequence of trees."""

def iq_simulate_alignment(tree: str, subst_model: str, rand_seed: int, partition_info: str, partition_type: str, seq_length: int, insertion_rate: float, deletion_rate: float, root_seq: str, num_threads: int, insertion_size_distribution: str, deletion_size_distribution: str, population_size: int) -> str:
    """Simulate an alignment with AliSim."""

def mine() -> int:
    """The meaning of life, the universe (and everything)!"""
