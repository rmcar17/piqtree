import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

from cogent3 import load_aligned_seqs

from piqtree import build_tree

TRIALS = 5


def benchmark_piqtree(trials: int) -> list[float]:
    times = []

    for trial in range(trials):
        print(
            f"\rDoing piq trial {trial + 1}/{trials}",
            "" if len(times) == 0 else f" last trial took {times[-1]:.2f}s",
            end="",
        )
        start = time.time()
        aln = load_aligned_seqs("aln_200_6000.fasta", moltype="dna")
        _ = build_tree(aln, "GTR+G", rand_seed=42)
        finish = time.time()
        times.append(finish - start)

    print("Piq trials completed. Times:", times)
    return times


def benchmark_iqtree(trials: int) -> list[float]:
    times = []

    for trial in range(trials):
        print(
            f"\rDoing IQ trial {trial + 1}/{trials}",
            "" if len(times) == 0 else f" last trial took {times[-1]:.2f}s",
            end="",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            cwdir = Path.cwd()

            shutil.copy("aln_200_6000.fasta", tmpdir + "/aln_200_6000.fasta")
            os.chdir(tmpdir)

            start = time.time()
            subprocess.check_output(
                [
                    f"/{cwdir}/iqtree3",
                    "-s",
                    "aln_200_6000.fasta",
                    "-m",
                    "GTR+G",
                    "-seed",
                    "42",
                    "-nt",
                    "1",
                ],
            )
            finish = time.time()
            times.append(finish - start)

            os.chdir(cwdir)

    print("IQ trials completed. Times:", times)
    return times


if __name__ == "__main__":
    iq_times = benchmark_iqtree(TRIALS)
    with open("bench_iq_times.csv", "w") as f:
        f.write(",".join(map(str, iq_times)))

    piq_times = benchmark_piqtree(TRIALS)
    with open("bench_piq_times.csv", "w") as f:
        f.write(",".join(map(str, piq_times)))
