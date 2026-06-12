# 🔍 Web Server Log Analysis — Failed Request Detection (Versão Atualizada)

> Sistema acadêmico para análise de logs de servidores web utilizando conceitos de Programação Distribuída e Concorrente, com foco na identificação de requisições com falha, detecção de padrões suspeitos e avaliação de desempenho através de processamento paralelo.

---

# 👥 Integrantes

| Nome | RA |
|--------|--------|
| Ana Júlia | 076130 |
| Vinícius Caetano de Assis | 075753 |

---

# 🎓 Informações Acadêmicas

| Campo | Informação |
|--------|--------|
| Curso | Análise e Desenvolvimento de Sistemas (ADS) |
| Disciplina | Programação Distribuída e Concorrente |

---

# 📌 Objetivo do Projeto

Este projeto tem como objetivo analisar grandes volumes de logs de servidores web para identificar requisições com falha (HTTP 4xx e 5xx), detectar possíveis padrões de comportamento suspeito e avaliar os ganhos de desempenho obtidos através do processamento paralelo.

O sistema foi desenvolvido para aplicar na prática conceitos de:

- Programação Concorrente
- Paralelismo
- Sistemas Distribuídos
- Processamento de Grandes Volumes de Dados
- Análise de Logs
- Balanceamento de Carga

---

# 🚀 Funcionalidades

- Leitura de arquivos de log de servidores web
- Identificação automática de códigos HTTP de erro
- Contabilização de falhas por endereço IP
- Associação IP → Hostname
- Geração do ranking dos IPs com mais falhas
- Processamento sequencial para comparação
- Processamento paralelo utilizando multiprocessing
- Medição de desempenho e comparação de tempos
- Geração de grandes bases de teste para benchmark

---

# 🛠 Tecnologias Utilizadas

| Tecnologia | Finalidade |
|------------|------------|
| Python 3 | Linguagem principal |
| Regex (re) | Extração de IPs e códigos HTTP |
| CSV | Leitura do mapeamento IP → Hostname |
| collections.Counter | Contagem eficiente |
| multiprocessing | Execução paralela |
| time | Benchmark de desempenho |

---

# 📂 Estrutura do Projeto

```text
projeto-logs/
│
├── algoritmo.py
│   ├── Implementação sequencial
│   ├── Processa o log linha por linha
│   └── Gera ranking dos IPs com mais falhas
│
├── paralelismo.py
│   ├── Implementação paralela
│   ├── Divide o log em blocos
│   ├── Utiliza multiprocessing.Pool
│   └── Compara desempenho entre diferentes quantidades de processos
│
├── multiplicador.py
│   ├── Ferramenta de geração de massa de testes
│   └── Replica arquivos de log para aumentar o volume de dados
│
├── access.log
│   └── Base principal de análise
│
├── client_hostname.csv
│   └── Relação entre IPs e hostnames
│
└── README.md
```

---

# 📊 Funcionamento

## Etapa 1 — Carregamento dos Dados

O sistema carrega:

- Arquivo de log (`access.log`)
- Arquivo de hostnames (`client_hostname.csv`)

---

## Etapa 2 — Identificação de Falhas

São considerados erros todos os códigos HTTP:

```text
4xx → Erros do Cliente
5xx → Erros do Servidor
```

Expressão regular utilizada:

```python
r"^(\d{1,3}(?:\.\d{1,3}){3}).*?\s([45]\d{2})\s"
```

---

## Etapa 3 — Contabilização

Para cada ocorrência:

- Extrai o IP
- Conta a ocorrência
- Armazena em estrutura Counter

---

## Etapa 4 — Ranking

Ao final da execução:

- Os IPs são ordenados pela quantidade de falhas
- É exibido o Top 10 de IPs com mais erros

---

# ▶ Como Executar

## 1. Instalar Python

Verifique a instalação:

```bash
python --version
```

ou

```bash
python3 --version
```

---

## 2. Preparar os Arquivos

Mantenha na mesma pasta:

```text
access.log
client_hostname.csv
algoritmo.py
paralelismo.py
```

---

## 3. Executar a Versão Sequencial

```bash
python algoritmo.py
```

ou

```bash
python3 algoritmo.py
```

---

## 4. Executar a Versão Paralela

```bash
python paralelismo.py
```

ou

```bash
python3 paralelismo.py
```

---

## 5. Gerar Massa de Testes

Configure os caminhos em:

```python
path_origem
path_destino
```

e execute:

```bash
python multiplicador.py
```

---

# 📈 Resultados Obtidos

O projeto permite comparar o desempenho da execução sequencial com a execução paralela utilizando diferentes quantidades de processos.

Exemplo:

```text
1 processo  → X segundos
2 processos → Y segundos
4 processos → Z segundos
8 processos → ...
12 processos → ...
```

Esses resultados permitem avaliar o impacto do paralelismo na análise de grandes arquivos de log.

---

# 🧠 Conceitos Aplicados

- Programação Concorrente
- Paralelismo
- Multiprocessamento
- Processamento de Logs
- Estruturas de Dados
- Expressões Regulares
- Balanceamento de Carga
- Benchmark de Desempenho
- Análise de Dados

---

# 🔗 Base de Dados

Dataset utilizado:

https://www.kaggle.com/datasets/eliasdabbas/web-server-access-logs/data

---

# 📄 Licença

Projeto desenvolvido exclusivamente para fins acadêmicos na disciplina de Programação Distribuída e Concorrente do curso de Análise e Desenvolvimento de Sistemas.
