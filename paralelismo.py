"""
paralelismo_v2.py — Análise paralela de logs de servidor web
Disciplina: Programação Distribuída e Concorrente

MELHORIAS EM RELAÇÃO À VERSÃO ORIGINAL:
=========================================
1. BYTE-RANGE CHUNKING (principal melhoria de eficiência)
   - Versão original: list(iter_chunks(...)) carregava TODO o log em RAM
     antes de começar, criando um gargalo serial enorme fora da medição.
   - Nova versão: cada processo recebe apenas (filepath, start_byte, end_byte)
     e abre o arquivo de forma INDEPENDENTE. Zero cópia de dados no pai.
   - Impacto: elimina o overhead serial de leitura, reduz pico de RAM de
     ~GBs para quase zero no processo pai.

2. imap_unordered em vez de pool.map
   - pool.map espera TODOS os workers terminarem para devolver resultados.
   - imap_unordered: o pai começa a REDUÇÃO assim que o 1° worker termina,
     sobrepondo CPU (redução) com I/O dos workers ainda em execução.

3. re.match em vez de re.search
   - search varre a string inteira até achar o padrão.
   - match ancora no início — para linhas sem IP no começo, falha mais rápido.

4. Regex simplificada — captura apenas grupo 1 (IP)
   - Versão original capturava grupo 2 (status) também, sem usar.

5. n=1 também usa Pool(1) — baseline consistente
   - Versão original usava loop puro para n=1, excluindo overhead de Pool
     e tornando a comparação injusta.

6. Tabela final inclui Eficiência (%) com marcação da meta do professor.

7. Labels corrigidos: "processos" em vez de "threads" (o código usa
   multiprocessing, não threading — erro técnico da versão original).
"""

import os
import re
import csv
import sys
import time
from collections import Counter
from multiprocessing import Pool, cpu_count

# ─────────────────────────────────────────────────────────────────
# REGEX compilada no nível do módulo (fora de qualquer função).
#
# Por estar aqui, é compilada UMA ÚNICA VEZ no processo pai e
# herdada pelos filhos via fork (Linux/macOS). No Windows (spawn),
# cada processo recompila ao importar o módulo — mesmo assim,
# compilar aqui evita recompilar a cada linha processada.
#
# re.match() ancora no início da string (^), evitando varredura
# desnecessária quando o IP não está no começo.
# Captura apenas grupo 1 (IP) — o status 4xx/5xx é verificado
# pela regex mas não capturado (sem group(2) desnecessário).
# ─────────────────────────────────────────────────────────────────
LOG_PATTERN = re.compile(
    r"^(\d{1,3}(?:\.\d{1,3}){3}).*?\s[45]\d{2}\s"
)


# ─────────────────────────────────────────────────────────────────
# FUNÇÃO TRABALHADORA — executa em processo SEPARADO
#
# Recebe (filepath, start_byte, end_byte).
# Abre o arquivo de forma INDEPENDENTE — nenhum dado é copiado
# do processo pai para o filho. O SO cuida do page cache.
#
# Descarte de linha parcial: se não somos o primeiro chunk,
# a primeira linha lida pode ser um fragmento (o seek caiu no
# meio de uma linha). Descartamos — ela foi contada pelo chunk
# anterior, que terminou exatamente nessa linha completa.
# ─────────────────────────────────────────────────────────────────
def process_byte_range(args: tuple) -> Counter:
    filepath, start, end = args
    local_counter = Counter()

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(start)

        if start != 0:
            f.readline()  # descarta linha parcial

        while True:
            pos = f.tell()
            if pos >= end:
                break
            line = f.readline()
            if not line:
                break
            match = LOG_PATTERN.match(line)
            if match:
                local_counter[match.group(1)] += 1

    return local_counter


# ─────────────────────────────────────────────────────────────────
# DIVISÃO EM BYTE-RANGES
#
# Calcula apenas os offsets de início e fim de cada fatia.
# Não lê nenhum dado — operação O(1) em tempo e memória.
# ─────────────────────────────────────────────────────────────────
def get_byte_ranges(filepath: str, n: int) -> list:
    size = os.path.getsize(filepath)
    chunk = size // n
    ranges = []
    start = 0
    for i in range(n):
        end = size if i == n - 1 else start + chunk
        ranges.append((filepath, start, end))
        start = end
    return ranges


# ─────────────────────────────────────────────────────────────────
# CARREGAMENTO DO CSV  ip -> hostname
# ─────────────────────────────────────────────────────────────────
def load_hosts(csv_path: str) -> dict:
    mapping = {}
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mapping[row["client"]] = row["hostname"]
        print(f"Mapeamento carregado: {len(mapping)} entradas.")
    except FileNotFoundError:
        print(f"[AVISO] '{csv_path}' nao encontrado — hostnames serao omitidos.")
    except KeyError as exc:
        print(f"[ERRO] Coluna ausente no CSV: {exc}")
        sys.exit(1)
    return mapping


# ─────────────────────────────────────────────────────────────────
# EXECUÇÃO DE UM TESTE COM N PROCESSOS
#
# imap_unordered: diferente de pool.map (que bloqueia até todos
# terminarem), imap_unordered entrega cada resultado assim que
# fica pronto. O processo pai reduz enquanto os outros workers
# ainda estão processando — sobreposição real de CPU e I/O.
# ─────────────────────────────────────────────────────────────────
def run_test(n_workers: int, log_file: str) -> tuple:
    ranges = get_byte_ranges(log_file, n_workers)
    total: Counter = Counter()

    t0 = time.perf_counter()

    with Pool(processes=n_workers) as pool:
        for partial in pool.imap_unordered(process_byte_range, ranges):
            total.update(partial)  # redução incremental

    elapsed = time.perf_counter() - t0
    return elapsed, total


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    LOG_FILE     = "access.log"
    CSV_FILE     = "client_hostname.csv"
    WORKER_COUNTS = [1, 2, 4, 8, 12]

    if not os.path.exists(LOG_FILE):
        print(f"[ERRO] Arquivo '{LOG_FILE}' nao encontrado.")
        sys.exit(1)

    size_mb = os.path.getsize(LOG_FILE) / 1_000_000
    print(f"CPUs detectadas : {cpu_count()} cores")
    print(f"Arquivo de log  : {LOG_FILE}  ({size_mb:.1f} MB)")
    print(f"Configuracoes   : {WORKER_COUNTS} processos\n")

    ip_to_host = load_hosts(CSV_FILE)

    tempos: dict = {}
    last_counts: Counter = Counter()

    for n in WORKER_COUNTS:
        print(f"Rodando com {n} processo(s)...", flush=True)
        elapsed, counts = run_test(n, LOG_FILE)
        tempos[n] = elapsed
        last_counts = counts
        print(f"  => {elapsed:.2f}s\n")

    # ── Top 10 IPs ──────────────────────────────────────────────
    sep = "=" * 65
    print(sep)
    print("  Top 10 IPs — mais requisicoes com falha (HTTP 4xx/5xx)")
    print(sep)
    for rank, (ip, count) in enumerate(last_counts.most_common(10), 1):
        host = ip_to_host.get(ip, "Desconhecido")
        print(f"  {rank:>2}. {ip:<17} {host:<28} {count:>7} falhas")
    print(sep)

    # ── Tabela de desempenho ─────────────────────────────────────
    baseline = tempos[1]
    print()
    print("=" * 65)
    print(f"  {'Processos':<12} {'Tempo (s)':<14} {'Speedup':<12} {'Eficiencia'}")
    print("-" * 65)
    for n, t in tempos.items():
        speedup = baseline / t
        efic    = speedup / n
        meta    = " <-- META ATINGIDA" if efic >= 0.60 else f"  (meta: >=60%)"
        print(f"  {n:<12} {t:<14.2f} {speedup:<12.2f} {efic:.1%}{meta}")
    print("=" * 65)
    print()
