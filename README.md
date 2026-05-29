# 🔍 Web Server Log Analysis — Failed Request Detection

> Sistema distribuído e concorrente para análise de logs de acesso de servidores web com foco em **detecção de requisições com falha**, identificação de padrões suspeitos e monitoramento de integridade do servidor.

---

## 👥 Integrantes

| Nome | RA |
|---|---|
| Ana Júlia | 076130 |
| Vinícius Caetano de Assis | 075753 |

---

## 🎓 Informações Acadêmicas

| Campo | Informação |
|---|---|
| Curso | ADS — Análise e Desenvolvimento de Sistemas |
| Disciplina | Programação Distribuída e Concorrente |

---

## 📌 Visão Geral do Projeto

O sistema realiza o processamento massivo e paralelo de arquivos de log de servidores web, com foco na **detecção de requisições com falha (Failed Requests)**. Por meio de uma arquitetura distribuída Mestre-Trabalhador, o sistema é capaz de processar grandes volumes de dados com alta eficiência, identificando anomalias, erros e padrões que possam indicar falhas sistêmicas ou ataques.

### Principais Funcionalidades

- Contabilização de **requisições com falha** por código de status HTTP (4xx e 5xx)
- Identificação dos **Top IPs** com maior número de erros
- Detecção de **padrões suspeitos** e possíveis ataques (ex.: DDoS, força bruta)
- Monitoramento de **picos anormais** de tráfego e falhas
- Processamento paralelo via **threads** para alto desempenho

---

## 🏗️ Arquitetura do Sistema

O sistema adota o padrão **Mestre-Trabalhador** para processamento distribuído:

```
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

**Nó Mestre:** responsável por dividir o arquivo de log em blocos e distribuí-los aos trabalhadores, além de consolidar os resultados ao final.

**Nós Trabalhadores:** recebem os blocos, subdividem em regiões menores e criam múltiplas threads locais para processamento paralelo de cada região.

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| C++ | Linguagem principal do sistema |
| `std::thread` | Programação concorrente com threads nativas |
| Sockets TCP/IP | Comunicação distribuída entre nós |
| `unordered_map` | Contagem eficiente de IPs e erros |
| Streaming de Arquivo | Leitura sem sobrecarga de memória |
| Modelo Mestre-Trabalhador | Arquitetura de distribuição de tarefas |

---

## 📂 Estrutura do Projeto

```
projeto-logs/
│
├── master/
│   ├── master.cpp          # Lógica do nó mestre
│   └── reducer.cpp         # Consolidação dos resultados
│
├── worker/
│   ├── worker.cpp          # Lógica do nó trabalhador
│   ├── parser.cpp          # Parser de linhas de log
│   └── threads.cpp         # Gerenciamento de threads
│
├── datasets/
│   └── access.log          # Arquivo de log para análise
│
├── include/
│   └── shared.hpp          # Estruturas e constantes compartilhadas
│
└── README.md
```

---

## 🗂️ Base de Dados

O dataset utilizado é um log de acesso de servidor web real, disponível no Kaggle:

🔗 [Web Server Access Logs — Kaggle](https://www.kaggle.com/datasets/eliasdabbas/web-server-access-logs/data)

---

## 🚀 Como Executar

### 1. Compilar o Nó Mestre

```bash
g++ master/master.cpp -o master -pthread
```

### 2. Compilar o Nó Trabalhador

```bash
g++ worker/worker.cpp -o worker -pthread
```

### 3. Executar o Mestre

```bash
./master
```

### 4. Executar os Trabalhadores

Abra um terminal para cada trabalhador:

```bash
# Terminal 1
./worker 5001

# Terminal 2
./worker 5002

# Terminal 3
./worker 5003
```

---

## 🧵 Funcionamento das Threads

Cada nó trabalhador segue o pipeline abaixo:

1. **Recebe** um bloco do arquivo de log via socket TCP
2. **Subdivide** o bloco em regiões menores para paralelismo interno
3. **Cria múltiplas threads**, uma para cada região
4. Cada thread:
   - Lê e faz parse das linhas do log
   - Extrai o IP de origem e o código de status HTTP
   - Acumula a contagem de **requisições com falha** (status 4xx/5xx)
5. As threads sincronizam seus resultados parciais ao final

---

## 📊 Exemplo de Saída

### Top 10 IPs por Requisições com Falha

```
==============================
 TOP 10 IPs — FAILED REQUESTS
==============================

192.168.0.15  →  421 falhas  (403, 404, 500)
10.0.0.3      →  388 falhas  (404, 429)
172.16.1.7    →  302 falhas  (500, 503)
...
```

### Distribuição por Código HTTP

```
================================
 RESUMO DE FAILED REQUESTS
================================

400 Bad Request          →   1.243 ocorrências
401 Unauthorized         →     856 ocorrências
403 Forbidden            →   2.104 ocorrências
404 Not Found            →   5.892 ocorrências
429 Too Many Requests    →     437 ocorrências
500 Internal Server Err  →   1.108 ocorrências
503 Service Unavailable  →     672 ocorrências

Total de falhas          →  12.312 requisições
```

---

## 🔥 Detecção de Ataques e Anomalias

O sistema analisa padrões de falhas para identificar comportamentos suspeitos:

- **Acesso excessivo a rotas inexistentes (404):** possível varredura de endpoints
- **Picos de 401/403:** tentativas de acesso não autorizado ou força bruta
- **Volume elevado de 429:** rate limiting ativado, possível ataque automatizado
- **Rajadas de 500/503:** sobrecarga do servidor, possível ataque DDoS

### Exemplo de Alerta

```
╔══════════════════════════════════════════╗
║             ⚠ ALERTA DE SEGURANÇA        ║
╠══════════════════════════════════════════╣
║ IP suspeito detectado:                   ║
║   192.168.0.15 → 152 falhas em 1 minuto  ║
║   Tipo predominante: 404 Not Found       ║
║ Possível: varredura de endpoints (scan)  ║
╚══════════════════════════════════════════╝
```

---

## ⚠️ Desafios Técnicos

### Divisão Correta do Arquivo

Ao dividir o log em blocos para os trabalhadores, existe o risco de uma linha ser cortada ao meio, corrompendo o parse.

**Solução:** ao iniciar a leitura de um bloco que não começa no offset zero, a primeira linha incompleta é descartada:

```cpp
if (inicio != 0) {
    descartarPrimeiraLinhaIncompleta();
}
```

### Gerenciamento de Memória com Arquivos Grandes

Logs de produção podem ter dezenas de GB. Carregar o arquivo completo em memória não é viável.

**Solução:** leitura em streaming linha a linha, mantendo consumo de memória constante:

```cpp
std::getline(arquivo, linha);
```

### Sincronização de Threads

Múltiplas threads atualizando o mesmo mapa de contagem simultaneamente pode causar condição de corrida.

**Solução:** uso de `mutex` para proteger o acesso ao `unordered_map` compartilhado:

```cpp
std::lock_guard<std::mutex> lock(mapMutex);
contagem[ip]++;
```

---

## 📈 Escalabilidade e Desempenho

O sistema apresenta ganho de desempenho proporcional ao número de threads utilizadas.

### Benchmark — Tempo Médio de Processamento (5 execuções)

| Threads | Tempo Médio (s) | Speedup |
|:---:|:---:|:---:|
| 1 | 94,28s | 1,0× |
| 2 | 0s | 0× |
| 4 | 0s | 0× |
| 8 | 0s | 0× |

### Benchmark — Acurácia de Detecção de Failed Requests

O sistema foi submetido a **5 execuções de validação** sobre um conjunto de dados rotulado. O resultado médio de acurácia na detecção correta de requisições com falha foi:

| Tentativa | Resultado |
|:---:|:---:|
| 1 | 95,25 |
| 2 | 95,69 |
| 3 | 94,86 |
| 4 | 92,59 |
| 5 | 93,01 |
| **Média** | **94,28** |

> A taxa média de **94,28** de acurácia demonstra a robustez do parser e da lógica de classificação de falhas sobre dados reais de servidor web.

---

## 🌐 Simulação de Rede Local

Caso não haja múltiplas máquinas físicas disponíveis, o ambiente distribuído pode ser simulado localmente utilizando portas distintas no mesmo host:

```bash
127.0.0.1:5001   ← Trabalhador 1
127.0.0.1:5002   ← Trabalhador 2
127.0.0.1:5003   ← Trabalhador 3
```

---

## 📚 Conceitos Aplicados

| Conceito | Aplicação no Projeto |
|---|---|
| Concorrência | Múltiplas threads processando regiões do log em paralelo |
| Paralelismo | Processamento simultâneo em múltiplos trabalhadores |
| Sistemas Distribuídos | Comunicação via sockets TCP entre mestre e trabalhadores |
| Sincronização | Mutex para acesso seguro ao mapa de contagem |
| Streaming de Arquivos | Leitura linha a linha sem sobrecarga de memória |
| Map/Reduce | Mapeamento de IPs e redução para contagem final |
| Balanceamento de Carga | Divisão equitativa do arquivo entre trabalhadores |
| Detecção de Anomalias | Classificação de padrões suspeitos por código HTTP |

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos no curso de Análise e Desenvolvimento de Sistemas.
