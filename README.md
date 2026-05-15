# ANÁLISE DE LOG WEB SERVER

## 👥 Integrantes

| Nome | RA |
|---|---|
| ANA JÚLIA | 076130 |
| VINÍCIUS CAETANO DE ASSIS | 075753 |

---

## 🎓 Informações Acadêmicas

- Curso: ADS (Análise e Desenvolvimento de Sistemas)
- Disciplina: Programação Distribuída e Concorrente

---

# 📌 Descrição do Projeto

O projeto “Análise de Log Web Server” consiste em um sistema distribuído e concorrente responsável por processar arquivos de logs de acesso de servidores web.

A aplicação utiliza:
- Programação concorrente com Threads;
- Programação distribuída utilizando modelo Mestre-Trabalhador;
- Processamento paralelo de grandes volumes de dados;
- Leitura eficiente de arquivos em streaming.

O sistema identifica:
- Frequência de acessos;
- Failed Request
- Top IPs com mais requisições;
- Possíveis padrões suspeitos de ataque.

---

# 🏗️ Arquitetura do Sistema

```text
               ┌─────────────────────┐
               │      Nó Mestre      │
               │  Distribui tarefas  │
               │ Consolida resultados│
               └─────────┬───────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼

 ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
 │ Trabalhador 1  │ │ Trabalhador 2  │ │ Trabalhador N  │
 │ Threads locais │ │ Threads locais │ │ Threads locais │
 └────────────────┘ └────────────────┘ └────────────────┘
```

---

# ⚙️ Tecnologias Utilizadas

- Python
- Threads (`std::thread`)
- Sockets TCP/IP
- HashMap (`unordered_map`)
- Programação Concorrente
- Programação Distribuída
- Streaming de Arquivos

---

# 📂 Estrutura do Projeto

```bash
projeto-logs/
│
├── master/
│   ├── master.cpp
│   └── reducer.cpp
│
├── worker/
│   ├── worker.cpp
│   ├── parser.cpp
│   └── threads.cpp
│
├── datasets/
│   └── access.log
│
├── include/
│   └── shared.hpp
│
└── README.md
```

---

# 🗂️ Base de Dados

```txt
LINK DA BASE DE DADOS:
[(https://www.kaggle.com/datasets/eliasdabbas/web-server-access-logs/data)]
```

---

# 🚀 Como Executar

## 1️⃣ Compilar o Nó Mestre

```bash
g++ master/master.cpp -o master -pthread
```

---

## 2️⃣ Compilar o Nó Trabalhador

```bash
g++ worker/worker.cpp -o worker -pthread
```

---

## 3️⃣ Executar o Mestre

```bash
./master
```

---

## 4️⃣ Executar os Trabalhadores

### Terminal 1

```bash
./worker 5001
```

### Terminal 2

```bash
./worker 5002
```

### Terminal 3

```bash
./worker 5003
```

---

# 🧵 Funcionamento das Threads

Cada trabalhador:
1. Recebe uma parte do arquivo;
2. Divide o bloco em regiões menores;
3. Cria múltiplas threads;
4. Cada thread:
   - lê uma região específica;
   - extrai os IPs;
   - contabiliza a frequência de acessos.

---

# 📊 Exemplo de Saída

```bash
TOP 10 IPS

192.168.0.15 -> 421 acessos
10.0.0.3     -> 388 acessos
172.16.1.7   -> 302 acessos
```

---

# 🔥 Detecção de Ataques

O sistema pode detectar:
- IPs com acessos excessivos;
- Possíveis ataques DDoS;
- Picos anormais de tráfego.

Exemplo:

```bash
[ALERTA]

IP suspeito detectado:
192.168.0.15 -> 152 acessos em 1 minuto
```

---

# ⚠️ Desafios Técnicos

## Divisão Correta do Arquivo

Ao dividir o arquivo em blocos, existe o risco de cortar uma linha ao meio.

### Solução

```cpp
if (inicio != 0) {
    descartarPrimeiraLinhaIncompleta();
}
```

---

## Gerenciamento de Memória

Arquivos grandes não devem ser carregados completamente na memória RAM.

### Solução

```cpp
std::getline(arquivo, linha);
```

A leitura em streaming reduz o consumo de memória.

---

# 📈 Escalabilidade

O projeto demonstra ganho de desempenho utilizando múltiplas threads.

| Threads | Tempo |
|---|---|
| 1 | 18s |
| 2 | 11s |
| 4 | 6s |
| 8 | 3s |

---

# 🌐 Simulação de Rede

Caso não existam múltiplas máquinas físicas, é possível simular o ambiente distribuído utilizando diferentes portas no mesmo computador.

```bash
127.0.0.1:5001
127.0.0.1:5002
127.0.0.1:5003
```
---

# 📚 Conceitos Aplicados

- Concorrência
- Paralelismo
- Sistemas Distribuídos
- Threads
- Sincronização
- Sockets
- Streaming de Arquivos
- Reduce / Map
- Balanceamento de Carga
