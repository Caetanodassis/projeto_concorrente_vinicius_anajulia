import re
import csv
import sys
import time
from collections import Counter
from multiprocessing import Pool

# -------------------------
# REGEX COMPILADA UMA VEZ
# Compilar fora da função evita recompilar a cada chunk processado.
# Captura: grupo 1 = IP, grupo 2 = código de status 4xx ou 5xx
# -------------------------
LOG_PATTERN = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}).*?\s([45]\d{2})\s")


# -------------------------
# FUNÇÃO TRABALHADORA
# Recebe uma lista de linhas (chunk) e retorna um Counter com
# a contagem de requisições com falha por IP.
# -------------------------
def process_chunk(lines: list[str]) -> Counter:
    local_counter = Counter()

    for line in lines:
        match = LOG_PATTERN.search(line)
        if match:
            local_counter[match.group(1)] += 1

    return local_counter


# -------------------------
# GERADOR DE CHUNKS
# Lê o arquivo linha a linha e emite chunks sem manter
# todo o conteúdo do log na memória ao mesmo tempo.
# -------------------------
def iter_chunks(filepath: str, chunk_size: int):
    current_chunk = []

    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            current_chunk.append(line)

            if len(current_chunk) == chunk_size:
                yield current_chunk
                current_chunk = []

    if current_chunk:
        yield current_chunk


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":

    CHUNK_SIZE = 50_000  # Linhas por bloco de processamento
    LOG_FILE = "access.log"
    CSV_FILE = "client_hostname.csv"

    # -------------------------
    # CARREGAR MAPEAMENTO IP → HOSTNAME
    # -------------------------
    ip_to_host: dict[str, str] = {}

    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ip_to_host[row["client"]] = row["hostname"]
        print(f"Mapeamento carregado: {len(ip_to_host)} entradas.")
    except FileNotFoundError:
        print(f"[ERRO] Arquivo '{CSV_FILE}' não encontrado. Continuando sem mapeamento de hostnames.")
    except KeyError as e:
        print(f"[ERRO] Coluna esperada não encontrada no CSV: {e}. Verifique o cabeçalho do arquivo.")
        sys.exit(1)

    # -------------------------
    # PRÉ-CARREGAR CHUNKS
    # Materializa os chunks em lista para reutilização nos múltiplos
    # testes de workers. Em produção (execução única), usar iter_chunks()
    # diretamente no Pool evitaria manter tudo na RAM.
    # -------------------------
    try:
        chunks = list(iter_chunks(LOG_FILE, CHUNK_SIZE))
    except FileNotFoundError:
        print(f"[ERRO] Arquivo de log '{LOG_FILE}' não encontrado.")
        sys.exit(1)

    print(f"Total de chunks: {len(chunks)} ({CHUNK_SIZE} linhas cada, aprox.)\n")

    # -------------------------
    # BENCHMARK: DIFERENTES QUANTIDADES DE WORKERS
    # Usa multiprocessing.Pool (processos, não threads) para contornar
    # o GIL do Python e obter paralelismo real em tarefas CPU-bound.
    # -------------------------
    worker_counts = [1, 2, 4, 8, 12]
    tempos: dict[int, float] = {}
    best_counts: Counter = Counter()
    best_time = float("inf")

    for n_workers in worker_counts:
        print(f"Rodando com {n_workers} worker(s)...")

        inicio = time.perf_counter()

        if n_workers == 1:
            # Execução sequencial (baseline para comparação)
            results = [process_chunk(chunk) for chunk in chunks]
        else:
            # Execução paralela: cada worker processa um chunk independente
            with Pool(n_workers) as pool:
                results = pool.map(process_chunk, chunks)

        # Redução: combina todos os contadores parciais em um único
        ip_counts: Counter = Counter()
        for r in results:
            ip_counts.update(r)

        fim = time.perf_counter()
        tempo = fim - inicio
        tempos[n_workers] = tempo

        print(f"  Tempo com {n_workers} worker(s): {tempo:.6f} segundos")

        # Salva o resultado da execução mais rápida
        if tempo < best_time:
            best_time = tempo
            best_counts = ip_counts

    # -------------------------
    # RESULTADO FINAL: TOP 10 IPs COM MAIS FALHAS
    # Exibe o resultado da execução mais rápida registrada.
    # -------------------------
    print("\n-----Top 10 IPs com mais requisições com falha-----")
    for rank, (ip, count) in enumerate(best_counts.most_common(10), 1):
        hostname = ip_to_host.get(ip, "Desconhecido")
        print(f"{rank:>2}. IP: {ip:<15} | Host: {hostname:<40} | Failed: {count}")

    # -------------------------
    # COMPARAÇÃO DE DESEMPENHO
    # -------------------------
    baseline = tempos.get(1, 1)
    print("\n===== COMPARAÇÃO DE DESEMPENHO =====")
    print(f"{'Workers':<10} {'Tempo (s)':<16} {'Speedup'}")
    print("-" * 38)
    for n, t in tempos.items():
        speedup = baseline / t if t > 0 else float("inf")
        print(f"{n:<10} {t:<16.6f} {speedup:.2f}x")
