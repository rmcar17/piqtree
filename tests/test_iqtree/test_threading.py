"""IQ-TREE isn't re-entrant, so concurrent calls from threads must be serialised.

These matter most on free-threaded Python, where there is no GIL to do so.
"""

import pathlib
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import pytest
from cogent3.core.alignment import Alignment
from cogent3.core.tree import PhyloNode

import piqtree
from piqtree import TreeGenMode
from piqtree.exceptions import IqTreeError

NUM_THREADS = 8
REPEATS = 4


def run_concurrently[T](funcs: list[Callable[[], T]]) -> list[T]:
    """Run the functions in separate threads, starting them all at once."""
    barrier = threading.Barrier(len(funcs))

    def run(func: Callable[[], T]) -> T:
        barrier.wait()
        return func()

    with ThreadPoolExecutor(max_workers=len(funcs)) as executor:
        return list(executor.map(run, funcs))


def test_concurrent_calls(
    four_otu: Alignment,
    five_trees: list[PhyloNode],
    four_taxon_unrooted_tree: PhyloNode,
) -> None:
    tree = piqtree.build_tree(four_otu, "JC", rand_seed=1)
    calls: list[Callable[[], str]] = [
        lambda: str(piqtree.build_tree(four_otu, "JC", rand_seed=1)),
        lambda: str(piqtree.fit_tree(four_otu, tree, "JC")),
        lambda: str(piqtree.random_tree(10, TreeGenMode.YULE_HARDING, rand_seed=1)),
        lambda: str(piqtree.robinson_foulds(five_trees).tolist()),
        lambda: str(piqtree.nj_tree(piqtree.jc_distances(four_otu))),
        lambda: str(
            piqtree.simulate_alignment(
                four_taxon_unrooted_tree,
                "JC",
                length=50,
                rand_seed=1,
            ).to_dict(),
        ),
        lambda: str(piqtree.consensus_tree(five_trees)),
    ]
    expected = [call() for call in calls]
    cwd = pathlib.Path.cwd()

    got = run_concurrently(calls * REPEATS)

    assert got == expected * REPEATS
    # The working directory is restored once all calls finish
    assert pathlib.Path.cwd() == cwd


def test_concurrent_errors(
    four_otu: Alignment,
    four_taxon_unrooted_tree: PhyloNode,
) -> None:
    # Errors in one thread are raised in that thread, and don't affect others
    def bad_call() -> None:
        # The tree's taxa don't match the alignment's
        with pytest.raises(IqTreeError):
            piqtree.fit_tree(four_otu, four_taxon_unrooted_tree, "JC")

    def good_call() -> None:
        piqtree.random_tree(5, TreeGenMode.BALANCED, rand_seed=1)

    run_concurrently([bad_call, good_call] * (NUM_THREADS // 2))
