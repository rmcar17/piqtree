import yaml
from _piqtree import iq_simulate_alignment
from cogent3 import make_aligned_seqs
from cogent3.core.alignment import Alignment
from cogent3.core.tree import PhyloNode

from piqtree.distribution import IndelDistribution
from piqtree.exceptions import ParseIqTreeError
from piqtree.iqtree._decorator import iqtree_func
from piqtree.model import Model, make_model
from piqtree.util import get_newick

iq_simulate_alignment = iqtree_func(iq_simulate_alignment, hide_files=True)


def simulate_alignment(
    tree: PhyloNode,
    model: Model | str,
    length: int = 1000,
    rand_seed: int | None = None,
    insertion_rate: float = 0.0,
    deletion_rate: float = 0.0,
    insertion_size_distribution: IndelDistribution | str = "POW{1.7/100}",
    deletion_size_distribution: IndelDistribution | str = "POW{1.7/100}",
    root_seq: str | None = None,
    num_threads: int | None = None,
) -> Alignment:
    """Uses AliSim to simulate an Alignment through IQ-TREE.

    Parameters
    ----------
    tree: list[cogent3.PhyloNode]
        A tree to simulate an alignment over.
    model: str
        The substitution model's specification.
    length: int
        The length of the alignment (by default 1000).
        Alignment may be longer when indel model is used due to insertion events.
    rand_seed : int | None, optional
        The random seed - 0 or None means no seed, by default None.
    insertion_rate: float | None, optional
        The insertion rate relative to substitution rate (by default 0.0).
    deletion_rate: float | None, optional
        The deletion rate relative to substitution rate (by default 0.0).
    insertion_size_distribution: str | None, optional
        The insertion size distribution (by default the Zipfian
        distribution with a=1.7 and maximum size 100).
    deletion_size_distribution: str | None, optional
        The deletion size distribution (by default the Zipfian
        distribution with a=1.7 and maximum size 100).
    root_seq: str | None, optional
        The root sequence (by default None).
    num_threads: int | None, optional
        Number of threads for IQ-TREE to use, by default None (single-threaded).

    Returns
    -------
    c3_types.AlignedSeqsType
        The simulated alignment.

    """
    if rand_seed is None:
        rand_seed = -1

    if root_seq is None:
        root_seq = ""

    if num_threads is None:
        num_threads = 1

    if isinstance(model, str):
        model = make_model(model)
    newick_tree = get_newick(tree)

    yaml_result = yaml.safe_load(
        iq_simulate_alignment(
            newick_tree,
            str(model),
            rand_seed,
            "",
            "",
            length,
            insertion_rate,
            deletion_rate,
            root_seq,
            num_threads,
            str(insertion_size_distribution),
            str(deletion_size_distribution),
            -1,
        ),
    )

    seqs = _parse_yaml_alignment(yaml_result["alignment"])

    return make_aligned_seqs(seqs, moltype=model.submod_type.get_moltype())


def _parse_yaml_alignment(yaml_alignment: str) -> dict[str, str]:
    seqs: dict[str, str] = {}
    name = None
    seq_buffer = None
    for part in yaml_alignment.split("\n"):
        if part.startswith(">"):
            if seq_buffer is not None:
                if name is None:
                    msg = "Got sequence data without name."
                    raise ParseIqTreeError(msg)
                seqs[name] = seq_buffer
            name = part.strip()[1:]
            seq_buffer = ""
        elif seq_buffer is not None:
            seq_buffer += part.strip()
        else:
            msg = f"Unexpected parsed value '{part}'"
            raise ParseIqTreeError(msg)

    if seq_buffer is not None:
        if name is None:
            msg = "Got sequence data without name."
            raise ParseIqTreeError(msg)
        seqs[name] = seq_buffer
    return seqs
