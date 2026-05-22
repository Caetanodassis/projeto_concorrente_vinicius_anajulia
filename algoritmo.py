import re
import csv
import time
from collections import Counter

# ✅ TEMPO INÍCIO
inicio = time.perf_counter()

# -------------------------
# 1. CARREGAR CSV (IP → HOST)
# -------------------------
ip_to_host = {}

with open("client_hostname.csv", newline='', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        ip_to_host[row["client"]] = row["hostname"]

# -------------------------
# 2. PROCESSAR LOG
# -------------------------
ip_counts = Counter()
line_counter = 0

# ✅ detecta TODOS failed requests
log_pattern = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}).*?\s([45]\d{2})\s")

with open("access.log", "r", encoding="utf-8", errors="ignore") as file:

    for line in file:
        match = log_pattern.search(line)

        if match:
            ip = match.group(1)
            ip_counts[ip] += 1

        line_counter += 1

        if line_counter % 100000 == 0:
            print(f"Processed: {line_counter} lines")

# -------------------------
# 3. RESULTADO FINAL
# -------------------------
print("\n-----Top 10 IP (com hostname)-----")

for rank, (ip, count) in enumerate(ip_counts.most_common(10), 1):
    hostname = ip_to_host.get(ip, "Desconhecido")
    print(f"{rank}. IP: {ip:<15} | Host: {hostname:<40} | Failed: {count}")

# -------------------------
# 4. TEMPO FINAL
# -------------------------
fim = time.perf_counter()

print(f"\nTotal de linhas: {line_counter}")
print(f"Tempo de execução: {fim - inicio:.6f} segundos")