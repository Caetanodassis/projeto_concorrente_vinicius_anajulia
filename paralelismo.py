import re
import csv
import time
from collections import Counter
from multiprocessing import Pool

# -------------------------
# FUNÇÃO
# -------------------------
def process_chunk(lines):
    local_counter = Counter()
    pattern = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}).*?\s([45]\d{2})\s")

    for line in lines:
        match = pattern.search(line)
        if match:
            local_counter[match.group(1)] += 1

    return local_counter

# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":

    # -------------------------
    # CARREGAR CSV
    # -------------------------
    ip_to_host = {}

    with open("client_hostname.csv", newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ip_to_host[row["client"]] = row["hostname"]

    # -------------------------
    # LER LOG
    # -------------------------
    chunk_size = 50000
    chunks = []
    current_chunk = []

    with open("access.log", "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            current_chunk.append(line)

            if len(current_chunk) == chunk_size:
                chunks.append(current_chunk)
                current_chunk = []

    if current_chunk:
        chunks.append(current_chunk)

    print(f"Total de chunks: {len(chunks)}")

    # -------------------------
    # TESTES
    # -------------------------
    thread_list = [1, 2, 4, 8, 12]
    tempos = {}

    # ✅ para guardar resultado final
    best_counts = None

    for n_threads in thread_list:
        print(f"\nRodando com {n_threads} threads...")

        inicio = time.perf_counter()

        if n_threads == 1:
            results = [process_chunk(chunk) for chunk in chunks]
        else:
            with Pool(n_threads) as pool:
                results = pool.map(process_chunk, chunks)

        ip_counts = Counter()
        for r in results:
            ip_counts.update(r)

        fim = time.perf_counter()
        tempo = fim - inicio
        tempos[n_threads] = tempo

        print(f"Tempo com {n_threads} threads: {tempo:.6f} segundos")

        # ✅ salva última execução (ou pode salvar a melhor)
        best_counts = ip_counts

    # -------------------------
    # RESULTADO FINAL (TOP 10)
    # -------------------------
    print("\n-----Top 10 IP (com hostname)-----")

    for rank, (ip, count) in enumerate(best_counts.most_common(10), 1):
        hostname = ip_to_host.get(ip, "Desconhecido")
        print(f"{rank}. IP: {ip:<15} | Host: {hostname:<40} | Failed: {count}")

    # -------------------------
    # COMPARAÇÃO
    # -------------------------
    print("\n===== COMPARAÇÃO =====")
    for n, t in tempos.items():
        print(f"{n} threads → {t:.6f} segundos")