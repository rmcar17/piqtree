import csv
from pathlib import Path
from statistics import mean


def read_bench(path: Path) -> tuple[list[float], list[float]]:
    times: list[float] = []
    peaks: list[float] = []
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if not row:
                continue
            t = row.get("time_s") or row.get("time") or row.get("times")
            p = row.get("peak_rss_bytes") or row.get("peak_bytes") or row.get("peak")
            if t is None or t.strip() == "":
                continue
            try:
                times.append(float(t))
            except ValueError:
                continue
            if p is None or p.strip() == "":
                peaks.append(0.0)
            else:
                try:
                    peaks.append(float(p))
                except ValueError:
                    peaks.append(0.0)
    return times, peaks


def summarise(label: str, times: list[float], peaks: list[float]) -> None:
    if not times:
        print(f"{label}: no time data")
        return
    t_min = min(times)
    t_mean = mean(times)
    t_max = max(times)
    print(f"{label} times: min {t_min:.6f}s, mean {t_mean:.6f}s, max {t_max:.6f}s")
    if peaks:
        p_min = min(peaks) / (1024**2)
        p_mean = mean(peaks) / (1024**2)
        p_max = max(peaks) / (1024**2)
        print(
            f"{label} peak RSS: min {p_min:.3f} MiB, mean {p_mean:.3f} MiB, max {p_max:.3f} MiB",
        )


if __name__ == "__main__":
    piq_file = Path("bench_piq_results.csv")
    iq_file = Path("bench_iq_results.csv")

    piq_times, piq_peaks = read_bench(piq_file) if piq_file.exists() else ([], [])
    iq_times, iq_peaks = read_bench(iq_file) if iq_file.exists() else ([], [])

    summarise("piq", piq_times, piq_peaks)
    summarise("IQ", iq_times, iq_peaks)
