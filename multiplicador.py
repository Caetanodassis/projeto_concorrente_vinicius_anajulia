# === TRIPLICAR ARQUIVO .LOG ===
# Informe o path do arquivo .log e o destino abaixo:

path_origem = "C:/Users/e615785/Downloads/programacao_paralela/access.log"
path_destino = "C:/Users/e615785/Downloads/programacao_paralela/access.logaccess_X4.log"

# Ler o arquivo original
with open(path_origem, 'r') as f:
    linhas = f.readlines()

print(f"Linhas no arquivo original: {len(linhas):,}")

# Triplicar: escrever as mesmas linhas 3 vezes
with open(path_destino, 'w') as f:
    for _ in range(3):
        f.writelines(linhas)

# Conferir resultado
with open(path_destino, 'r') as f:
    total = sum(1 for _ in f)

print(f"Linhas no arquivo triplicado: {total:,}")
print(f"Fator de multiplicação: {total / len(linhas):.0f}x")
print(f"\nArquivo salvo em: {path_destino}")