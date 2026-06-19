"""
paralelismo_v4_pro.py

Melhorias:
✔ I/O ultra eficiente com mmap (memory-mapped file)
✔ Regex mais robusta (suporta mais formatos)
✔ Menos overhead de leitura
✔ Melhor compatibilidade com logs diferentes
✔ Estrutura mais modular e robusta
"""

import os
import re
import time
import mmap
from collections import Counter
from multiprocessing import Pool, cpu_count

# 🔥 Regex mais robusta (Apache, Nginx, etc.)
LOG_PATTERN = re.compile(
    r"""
    ^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})   # IP
    .*?                                 # qualquer coisa
    \s(?P<status>[1-5]\d{2})\s          # código HTTP
    """,
    re.VERBOSE,
)


def process_chunk(args):
    filepath, start, end = args
    counter = Counter()

    with open(filepath, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

        mm.seek(start)

        # evitar cortar linha pela metade
        if start != 0:
            mm.readline()

        while True:
            pos = mm.tell()
            if pos >= end:
                break

            line = mm.readline()
            if not line:
                break

            try:
                line = line.decode("utf-8", errors="ignore")
            except:
                continue

            match = LOG_PATTERN.match(line)
            if match:
                status = int(match.group("status"))

                # só erros 4xx e 5xx
                if 400 <= status <= 599:
                    ip = match.group("ip")
                    counter[ip] += 1

    return counter


def get_chunks(filepath, n_chunks):
    size = os.path.getsize(filepath)
    chunk_size = size // n_chunks

    ranges = []
    start = 0

    for i in range(n_chunks):
        end = size if i == n_chunks - 1 else start + chunk_size
        ranges.append((filepath, start, end))
        start = end

    return ranges


def parallel_process(filepath, n_workers):
    n_chunks = n_workers * 4
    ranges = get_chunks(filepath, n_chunks)

    total = Counter()
    start_time = time.perf_counter()

    with Pool(n_workers) as pool:
        for result in pool.imap_unordered(process_chunk, ranges, chunksize=2):
            total.update(result)

    elapsed = time.perf_counter() - start_time
    return total, elapsed


if __name__ == "__main__":

    FILE = "access_log_base_maior.log"
    WORKERS = [1, 2, 4, 8, 12]

    if not os.path.exists(FILE):
        print("Arquivo não encontrado!")
        exit()

    print(f"CPUs disponíveis: {cpu_count()}")
    print(f"Tamanho arquivo: {os.path.getsize(FILE)/1e6:.2f} MB\n")

    times = {}
    final_counts = Counter()

    for n in WORKERS:
        print(f"Executando com {n} processos...")
        counts, t = parallel_process(FILE, n)
        times[n] = t
        final_counts = counts
        print(f"Tempo: {t:.2f}s\n")

    # 🔝 Top IPs
    print("\nTOP 10 IPs com erros:")
    for i, (ip, c) in enumerate(final_counts.most_common(10), 1):
        print(f"{i:2d}. {ip:<15} {c} erros")

    # 📊 Performance
    baseline = times[1]
    print("\nPerformance:")
    print(f"{'Proc':<6} {'Tempo':<10} {'Speedup':<10} {'Eficiência'}")

    for n, t in times.items():
        speedup = baseline / t
        efficiency = speedup / n
        print(f"{n:<6} {t:<10.2f} {speedup:<10.2f} {efficiency:.1%}")
