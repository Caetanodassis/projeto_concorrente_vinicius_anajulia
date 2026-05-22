import re
import csv
import time
from collections import Counter

# INÍCIO DA MEDIÇÃO
inicio = time.perf_counter()

# ---------------------
# 1. CARREGAR HOSTNAMES
# ---------------------
ip_to_host = {}

with open("C:/Users/e615785/Downloads/programacao_paralela/client_hostname.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        ip_to_host[row["client"]] = row["hostname"]

# ---------------------
# 2. PROCESSAR ACCESS LOG
# ---------------------
ip_counts = Counter()

log_pattern = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}).*?\s(403|404)\s")

with open("C:/Users/e615785/Downloads/programacao_paralela/access.log", "r", encoding="utf-8", errors="ignore") as file:
    for line in file:
        match = log_pattern.search(line)

        if match:
            ip = match.group(1)
            ip_counts[ip] += 1

# ---------------------
# 3. PRINT RESULTADO + HOSTNAME
# ---------------------
print("-----Top 10 IP (com hostname)-----")

for rank, (ip, count) in enumerate(ip_counts.most_common(10), 1):
    hostname = ip_to_host.get(ip, "Desconhecido")
    print(f"{rank}. IP: {ip:<15} | Host: {hostname:<30} | Erros: {count}")

# FIM DA MEDIÇÃO
fim = time.perf_counter()

# RESULTADO DO TEMPO
tempo_total = fim - inicio
print(f"\nTempo de execução: {tempo_total:.6f} segundos")