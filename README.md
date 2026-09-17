# Mini Desafio Semana 7 — Análise de Vendas do Setor Varejista

![Python](https://img.shields.io/badge/Python-3.14-blue)
![pandas](https://img.shields.io/badge/pandas-latest-150458)
![matplotlib](https://img.shields.io/badge/matplotlib-latest-11557c)
![seaborn](https://img.shields.io/badge/seaborn-latest-4c72b0)
![License](https://img.shields.io/badge/License-MIT-yellow)

Análise exploratória de dados de vendas de uma rede de supermercados, com foco em sazonalidade, comportamento de compra e perfil do cliente.

**Curso:** SCTEC — Etapa Profissionalizar
**Autor:** [to-feature-or-not](https://github.com/to-feature-or-not)
**Data:** 2026-09-10

---

## 📋 Sobre o projeto

Este projeto realiza uma análise completa de um dataset de vendas do setor varejista, cobrindo o período de **2019 a 2022**.

O dataset original possui **830.000 registros brutos** (cada linha = 1 item comprado). Após agrupar duplicatas em uma coluna `QUANTITY`, a base final fica com **733.447 registros** (cada linha = 1 produto distinto por compra).

O pipeline inclui:

- Limpeza e tratamento de dados faltantes
- Conversão e validação de datas
- Detecção e agrupamento de duplicatas
- Análises de sazonalidade, produtos, categorias e clientes
- Geração de gráficos e relatórios

---

## 🧠 Reflexão teórica: ETL e qualidade de dados

### O que é ETL?

**ETL** (Extract, Transform, Load) é o processo fundamental em análise de dados:

- **Extract (Extrair):** obter dados de fontes diversas (CSV, banco, API)
- **Transform (Transformar):** limpar, padronizar, enriquecer e validar
- **Load (Carregar):** salvar em destino final (banco, dashboard, arquivo)

Neste projeto, o ETL foi aplicado assim:

| Etapa | O que foi feito |
|-------|-----------------|
| Extract | Leitura do `varejo.csv` com `pd.read_csv()` |
| Transform | Tratamento de `#N/D`, conversão de datas, agrupamento de duplicatas |
| Load | Salvamento em `data/processed/varejo_final.csv` |

### Por que qualidade de dados importa?

Dados brutos **raramente** estão prontos para análise. Problemas comuns:

- **Valores nulos (NaN)** — quebram cálculos e distorcem métricas
- **Marcadores textuais** (`#N/D`, `N/A`) — não são reconhecidos como nulos pelo pandas
- **Tipos incorretos** (data como texto) — impedem análise temporal
- **Duplicatas** — inflam contagens

Sem tratamento, **decisões baseadas nesses dados podem estar erradas**.

### Decisões tomadas neste projeto

- **Categorias vazias** → preenchidas com `"Sem Categoria"` para preservar os registros
- **Duplicatas** → **agrupadas** em vez de removidas, porque cada linha repetida representa **um item a mais na mesma compra** (não erro do sistema). Isso preserva o volume real de vendas em uma nova coluna `QUANTITY`.
- **Datas inválidas** → validadas e tratadas com `pd.to_datetime()`.

### Conclusão

Um pipeline ETL bem documentado garante **reprodutibilidade**, **transparência** e **confiabilidade** nas análises.

---

## 📁 Estrutura do projeto

```
Miniprojeto_MarielaCantero_Analise_de_Dados_T6
├── README.md
├── README_MarielaCantero_Analise_de_Dados_T6.md
├── DOCUMENTACAO.md 
├── LICENSE
├── requirements.txt
├── .gitignore
├── .gitattributes
├── Miniprojeto_MarielaCantero_Analise_de_Dados_T6.py
├── docs/
│   ├── descricao_base_de_dados_mini_projeto_M1_S7.pdf
│   └── enunciado_mini_projeto_M1_S7.pdf
└── data/
    ├── raw/
    │   └── varejo.csv
    ├── processed/
    │   └── varejo_final.csv
    └── output/
        ├── run_*.log
        └── grafico_*.png
```

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.14**
- **pandas** — manipulação e análise de dados
- **matplotlib** — visualização de dados
- **seaborn** — heatmaps de sazonalidade e de categoria × segmento

---

## 🚀 Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/to-feature-or-not/Miniprojeto_MarielaCantero_Analise_de_Dados_T6.git
cd Miniprojeto_MarielaCantero_Analise_de_Dados_T6
```

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\Activate.ps1
```

No Linux/Mac:

```bash
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Executar o script

```bash
python Miniprojeto_MarielaCantero_Analise_de_Dados_T6.py
```

Os resultados serão salvos em `data/output/` (gráficos + log) e `data/processed/` (CSV final).

---

## 🧹 Etapas do pipeline

| Etapa | Descrição |
|-------|-----------|
| 1. Carregamento | Leitura do CSV original (830.000 registros brutos) |
| 2. Exploração | Análise da estrutura e amostra dos dados |
| 3. Limpeza | Remoção de colunas vazias e preenchimento de `#N/D` com "Sem Categoria" |
| 4. Datas | Conversão e validação de datas |
| 5. Duplicatas | Agrupamento em coluna `QUANTITY` → 733.447 registros finais |
| 6. Análise | Sazonalidade (mês, ano, dia da semana), produtos, categorias, gênero, segmento, Pareto de clientes, tickets e categoria × segmento — 13 agrupamentos no total (10 com `groupby()`, 3 com `pivot_table()`) |
| 7. Visualização | 13 gráficos gerados automaticamente |
| 8. Relatório | Log completo + conclusões |

---

## 📊 Principais Insights

1. **Produto mais vendido:** Presunto Cozido (14.381 unidades)
2. **Categoria mais vendida:** Alimentos (52,4% das vendas)
3. **Mês com mais vendas:** Janeiro (83.963 unidades)
4. **Ano com mais vendas:** 2021 (245.259 unidades)
5. **Gênero com mais compras:** Feminino (52,1% das vendas)
6. **Segmento principal:** B (63,9% das vendas)

### 🛍️ Preferências por gênero

- **Mulheres (F):** Presunto Cozido, Sardinha, Detergente, Chupeta, Removedor
- **Homens (M):** Presunto Cozido, Banana, Refrigerante, Preservativo, Bife de Coxão Mole

### 📈 Análises complementares

- **Perfil familiar:** 52,5% dos clientes não têm filhos; média de 1,15 filhos por cliente
- **Média de itens por compra:** 44,94 itens
- **Top produto está distribuído** entre 1.000 clientes únicos (não concentrado)
- **Pareto de clientes (80/20):** identifica qual % de clientes concentra 80% das vendas
- **Padrão por dia da semana:** revela o melhor e o pior dia de vendas
- **Ticket médio por segmento e gênero:** mostra diferenças no valor gasto por visita
- **Categoria × Segmento:** cruza demanda por categoria e perfil econômico do cliente
- **Dispersão frequência × ticket:** classifica clientes em VIP, frequente, ocasional e esporádico
- **Tamanho das compras:** distribuição do número de itens por compra

---

### 📸 Visualizações

**Vendas por mês (sazonalidade):**
![Vendas por mês](data/output/grafico_sazonalidade.png)

**Heatmap de sazonalidade (mês × ano):**
![Heatmap](data/output/grafico_heatmap_sazonalidade.png)

**Top 10 produtos mais vendidos:**
![Top produtos](data/output/grafico_top_produtos.png)

**Vendas por categoria:**
![Categorias](data/output/grafico_categorias.png)

**Distribuição por gênero:**
![Gênero](data/output/grafico_genero.png)

**Vendas por segmento de cliente:**
![Segmento](data/output/grafico_segmento.png)

## 📈 Gráficos gerados

| Arquivo | Descrição |
|---------|-----------|
| `grafico_sazonalidade.png` | Vendas por mês (barras) |
| `grafico_heatmap_sazonalidade.png` | Heatmap mês × ano (seaborn) |
| `grafico_top_produtos.png` | Top 10 produtos (barras horizontais) |
| `grafico_categorias.png` | Vendas por categoria |
| `grafico_genero.png` | Distribuição por gênero (pizza) |
| `grafico_segmento.png` | Vendas por segmento de cliente |
| `grafico_ano.png` | Vendas por ano (barras) |
| `grafico_dia_semana.png` | Vendas por dia da semana (barras) |
| `grafico_pareto_clientes.png` | Curva de Pareto — concentração de clientes |
| `grafico_heatmap_categoria_segmento.png` | Heatmap categoria × segmento (seaborn) |
| `grafico_tamanho_compra.png` | Distribuição do tamanho das compras (itens/compra) |
| `grafico_filhos.png` | Distribuição do número de filhos por registro |
| `grafico_scatter_cliente.png` | Dispersão frequência × ticket médio (quadrantes VIP/esporádico) |

---

## 📝 Notas sobre os dados

### 🏷️ Produto sem cadastro

Todos os valores `#N/D` (3.650 registros, 0,44%) pertenciam a um único produto (`PR_ID = 107`), que não tinha nome nem categoria registrados.

- **Decisão:** preencher com `"Sem Categoria"` para preservar os registros.
- **Recomendação:** completar o cadastro do produto 107 na base de origem.

### 🔢 Dois números de registros

- **830.000** → registros brutos no CSV (cada linha = 1 item comprado)
- **733.447** → registros após agrupar duplicatas (cada linha = 1 produto por compra, com `QUANTITY` ≥ 1)

A soma da coluna `QUANTITY` reconstrói os 830.000 itens originais.

### 📅 Cobertura por ano

| Ano | Registros |
|-----|-----------|
| 2019 | 176.103 (24,0%) |
| 2020 | 192.804 (26,3%) |
| 2021 | 216.813 (29,6%) |
| 2022 | 147.727 (20,1%) |

2022 tem menos registros que os outros anos — vale investigar se é uma lacuna real ou apenas dado incompleto.

### 🔍 Distribuição do `#N/D`

- A distribuição de `#N/D` por data mostra valores repetidos (24, 26, 25...)
- Isso sugere que os dados podem ser sintéticos ou gerados aleatoriamente

---

## ⚠️ Limitações

- Sem coluna de preço → não é possível analisar faturamento
- `QUANTITY` inferida a partir de duplicatas (pode não ser 100% precisa)
- 2022 com menos dados que os demais anos

---

## 📌 Recomendações

1. Obter dados de preço para análises financeiras
2. Validar com a fonte se as duplicatas são realmente quantidade de produtos
3. Investigar a lacuna de dados em 2022
4. Completar o cadastro do produto 107 no sistema de origem

---

## 📄 Documentação completa

Para análise detalhada, insights completos e metodologia, consulte [DOCUMENTACAO.md](DOCUMENTACAO.md).

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Mariela Cantero** — [@to-feature-or-not](https://github.com/to-feature-or-not)
Mini-projeto avaliativo — Setembro/2026