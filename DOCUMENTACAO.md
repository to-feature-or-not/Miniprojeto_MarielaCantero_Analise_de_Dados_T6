# Documentação — Análise de Vendas do Setor Varejista

Documentação detalhada do mini-projeto de análise exploratória de dados de vendas do setor varejista (2019–2022).

**Curso:** SCTEC — Etapa Profissionalizar
**Autor:** [to-feature-or-not](https://github.com/to-feature-or-not)
**Data:** 2026-09-10

---

## 🎯 Objetivo

Este documento complementa o [`README.md`](README.md) com os detalhes técnicos da análise:
etapas do pipeline, insights completos, agrupamentos utilizados, visualizações, 
notas sobre os dados e limitações.

> **Nota sobre registros:** o CSV original tem **830.000 linhas** (1 item por linha). 
> Após agrupar duplicatas, a base final tem **733.447 registros** — a coluna `QUANTITY` 
> indica quantas unidades idênticas foram agrupadas.

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

## 🔗 Mapeamento: análise ↔ função no código

Esta tabela liga cada análise complementar ao bloco de código responsável por ela, 
facilitando a auditoria e a reprodução dos resultados. As análises **essenciais** já 
estão listadas na seção **"Agrupamentos utilizados"** mais abaixo.

| Análise | Descrição | Função no código |
|---------|-----------|------------------|
| Pareto de clientes | Identifica qual % de clientes concentra 80% das vendas | `analyze_customer_pareto()` |
| Dia da semana | Melhor e pior dia de vendas | `analyze_sales_by_weekday()` |
| Ticket médio por segmento | Valor médio gasto por visita, por segmento econômico | `analyze_avg_ticket_by_group()` |
| Ticket médio por gênero | Valor médio gasto por visita, por gênero | `analyze_avg_ticket_by_group()` |
| Categoria × Segmento | Cruzamento de demanda por categoria e segmento | `analyze_category_by_segment()` |
| Dispersão frequência × ticket | Classifica clientes em VIP, frequente, ocasional e esporádico | `analyze_customer_scatter()` |
| Tamanho das compras | Distribuição do número de itens por compra | `analyze_purchase_size()` |
| Concentração do produto top | Verifica se o produto top está concentrado em poucos clientes | `analyze_product_concentration()` |
| Cobertura por ano | Contagem de registros por ano (checagem de lacunas) | `analyze_records_by_year()` |
| Top produtos por gênero | Produtos mais comprados por homens e mulheres | `analyze_products_by_gender()` |
| Filhos do cliente | Estatísticas de `CL_FHL` (média, mediana, moda, desvio, quartis) | `analyze_children()` |

---

### 🔀 Agrupamentos utilizados

O enunciado pede "pelo menos dois agrupamentos usando `groupby()` ou `pivot_table()`". 
Este projeto utiliza **13 agrupamentos**, sendo 10 com `groupby()` e 3 com `pivot_table()`:

| # | Agrupamento | Função | Método |
|---|---|---|---|
| 1 | Vendas por mês | `analyze_sales_by_month()` | `groupby()` |
| 2 | Vendas por ano | `analyze_sales_by_year()` | `groupby()` |
| 3 | Vendas por dia da semana | `analyze_sales_by_weekday()` | `groupby()` |
| 4 | Top produtos | `analyze_top_products()` | `groupby()` |
| 5 | Top categorias | `analyze_top_categories()` | `groupby()` |
| 6 | Vendas por gênero | `analyze_sales_by_gender()` | `groupby()` |
| 7 | Vendas por segmento | `analyze_sales_by_segment()` | `groupby()` |
| 8 | Top produtos por gênero | `analyze_products_by_gender()` | `groupby()` |
| 9 | Pareto de clientes | `analyze_customer_pareto()` | `groupby()` |
| 10 | Ticket médio por grupo | `analyze_avg_ticket_by_group()` | `groupby()` |
| 11 | Categoria × Segmento | `analyze_category_by_segment()` | `pivot_table()` |
| 12 | Mês × Ano (heatmap) | `plot_seasonality_heatmap()` | `pivot_table()` |
| 13 | Categoria × Segmento (heatmap) | `plot_heatmap_category_segment()` | `pivot_table()` |

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

---

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

| Métrica | Valor |
|---|---|
| Registros brutos (CSV) | 830.000 |
| Registros após agrupamento | 733.447 |
| Redução | 11,63% (96.553 linhas agrupadas) |
| Soma de `QUANTITY` | 830.000 (reconstrói o total original) |

Cada linha do CSV representa **um item comprado**. Ao agrupar por `DATA + CO_ID + PR_ID`, 
itens idênticos na mesma compra são consolidados em `QUANTITY` (de 1 a 6).

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

## 👨‍👩‍👧 Estatísticas de Perfil Familiar (CL_FHL)

| Métrica | Valor |
|---------|-------|
| Média | 1,15 |
| Mediana | 0 |
| Moda | 0 |
| Desvio Padrão | 1,42 |
| Máximo | 4 |
| Mínimo | 0 |
| Contagem | 733.447 |

**Quartis:**

| Quartil | Valor |
|---------|-------|
| 25% (Q1) | 0 |
| 50% (Q2 - Mediana) | 0 |
| 75% (Q3) | 2 |

**Distribuição:**

| Filhos | Clientes | % |
|--------|----------|---|
| 0 | 384.986 | 52,5% |
| 1 | 90.845 | 12,4% |
| 2 | 94.168 | 12,8% |
| 3 | 92.407 | 12,6% |
| 4 | 71.041 | 9,7% |

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