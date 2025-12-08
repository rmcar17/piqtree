import os
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import psutil

from cogent3 import load_aligned_seqs
from piqtree import build_tree

TRIALS = 5
SAMPLE_INTERVAL = 0.01  # seconds


class PeakMonitor:
    def __init__(self, pid: int, interval: float = SAMPLE_INTERVAL) -> None:
        self.pid = pid
        self.interval = interval
        self._stop = threading.Event()
        self._peak = 0
        self._thread: threading.Thread | None = None

    def _sample(self) -> None:
        try:
            proc = psutil.Process(self.pid)
        except psutil.NoSuchProcess:
            return
        while not self._stop.is_set():
            try:
                children = proc.children(recursive=True)
                rss = proc.memory_info().rss
                for c in children:
                    try:
                        rss += c.memory_info().rss
                    except psutil.NoSuchProcess:
                        pass
                if rss > self._peak:
                    self._peak = rss
            except psutil.NoSuchProcess:
                break
            time.sleep(self.interval)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    @property
    def peak(self) -> int:
        return self._peak


def measure_callable_peak(func, *args, interval: float = SAMPLE_INTERVAL):
    pid = os.getpid()
    monitor = PeakMonitor(pid, interval=interval)
    monitor.start()
    t0 = time.perf_counter()
    result = func(*args)
    t1 = time.perf_counter()
    monitor.stop()
    return result, t1 - t0, monitor.peak


def run_subprocess_and_monitor(cmd: list[str], cwd: str | None = None, interval: float = SAMPLE_INTERVAL):
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    monitor = PeakMonitor(proc.pid, interval=interval)
    monitor.start()
    t0 = time.perf_counter()
    stdout, stderr = proc.communicate()
    t1 = time.perf_counter()
    monitor.stop()
    return proc.returncode, stdout, stderr, t1 - t0, monitor.peak


def benchmark_piqtree(trials: int) -> list[dict]:
    results: list[dict] = []
    for trial in range(1, trials + 1):
        print(f"\rDoing piq trial {trial}/{trials}", end="", flush=True)

        def job():
            aln = load_aligned_seqs("aln_200_6000.fasta", moltype="dna")
            tree = build_tree(aln, "GTR+G", rand_seed=42)
            return tree

        _, elapsed, peak = measure_callable_peak(job)
        results.append({"trial": trial, "time_s": elapsed, "peak_rss_bytes": peak})
        last = results[-1]
        print(f" last: {last['time_s']:.2f}s, peak {last['peak_rss_bytes'] / (1024**2):.2f} MiB", end="\n")
    return results


def benchmark_iqtree(trials: int) -> list[dict]:
    results: list[dict] = []
    cwdir = Path.cwd()
    iq_exe = cwdir / "iqtree3"
    if not iq_exe.exists():
        raise FileNotFoundError(f"IQ-TREE executable not found at {iq_exe}")

    for trial in range(1, trials + 1):
        print(f"\rDoing IQ trial {trial}/{trials}", end="", flush=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy("aln_200_6000.fasta", Path(tmpdir) / "aln_200_6000.fasta")
            cmd = [
                str(iq_exe),
                "-s",
                "aln_200_6000.fasta",
                "-m",
                "GTR+G",
                "-seed",
                "42",
                "-nt",
                "1",
            ]
            code, stdout, stderr, elapsed, peak = run_subprocess_and_monitor(cmd, cwd=tmpdir)
            if code != 0:
                out = stdout.decode(errors="ignore")
                err = stderr.decode(errors="ignore")
                raise subprocess.CalledProcessError(code, cmd, output=out, stderr=err)
            results.append({"trial": trial, "time_s": elapsed, "peak_rss_bytes": peak})
            last = results[-1]
            print(f" last: {last['time_s']:.2f}s, peak {last['peak_rss_bytes'] / (1024**2):.2f} MiB", end="\n")
    return results


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("trial,time_s,peak_rss_bytes,peak_rss_mib\n")
        for r in rows:
            f.write(
                f"{r['trial']},{r['time_s']:.6f},{r['peak_rss_bytes']},{r['peak_rss_bytes'] / (1024**2):.6f}\n"
            )


if __name__ == "__main__":
    piq_results = benchmark_piqtree(TRIALS)
    write_csv(Path("bench_piq_results.csv"), piq_results)

    iq_results = benchmark_iqtree(TRIALS)
    write_csv(Path("bench_iq_results.csv"), iq_results)

    def summarize(rows: list[dict]) -> None:
        times = [r["time_s"] for r in rows]
        peaks = [r["peak_rss_bytes"] for r in rows]
        print(f"trials: {len(rows)}, time mean {sum(times)/len(times):.3f}s, time min {min(times):.3f}s, time max {max(times):.3f}s")
        print(f"peak mean {sum(peaks)/len(peaks)/(1024**2):.3f} MiB, peak min {min(peaks)/(1024**2):.3f} MiB, peak max {max(peaks)/(1024**2):.3f} MiB")

    print("\nPIQTREE summary:")
    summarize(piq_results)
    print("\nIQTREE summary:")
    summarize(iq_results)
