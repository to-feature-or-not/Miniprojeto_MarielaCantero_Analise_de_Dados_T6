# Documentação — Análise de Vendas do Setor Varejista

Documentação detalhada do mini-projeto de análise exploratória de dados de vendas do setor varejista (2019–2022).

**Curso:** SCTEC — Etapa Profissionalizar
**Autor:** [to-feature-or-not](https://github.com/to-feature-or-not)
**Data:** 2026-09-10

---

## 🎯 Objetivo

Este documento complementa o [`README.md`](README.md) com os detalhes técnicos da análise:
etapas do pipeline, insights completos, visualizações, notas sobre os dados e limitações.

---

## 🧹 Etapas do pipeline

| Etapa | Descrição |
|-------|-----------|
| 1. Carregamento | Leitura do CSV original (830.000 registros) |
| 2. Exploração | Análise da estrutura e amostra dos dados |
| 3. Limpeza | Remoção de colunas vazias e preenchimento de `#N/D` com "Sem Categoria" |
| 4. Datas | Conversão e validação de datas |
| 5. Duplicatas | Agrupamento em coluna `QUANTITY` |
| 6. Análise | Sazonalidade, produtos, categorias, clientes, perfil |
| 7. Visualização | 6 gráficos gerados automaticamente |
| 8. Relatório | Log completo + conclusões |

---

## 📊 Principais Insights

1. **Produto mais vendido:** Presunto Cozido (14.381 unidades)
2. **Categoria mais vendida:** Alimentos (52,4% das vendas)
3. **Mês com mais vendas:** Janeiro (83.963 unidades)
4. **Ano com mais vendas:** 2021 (245.259 unidades)
5. **Gênero com mais compras:** Feminino (52,1% das vendas)
6. **Segmento principal:** B (63,9% das vendas)
7. **Média de itens por compra:** 44,94 itens
8. **Top produto está distribuído** entre 1.000 clientes únicos (não concentrado)
9. **Perfil familiar:** 52,5% dos clientes não têm filhos; média de 1,15 filhos por cliente

### 🛍️ Preferências por gênero

- **Mulheres (F):** Presunto Cozido, Sardinha, Detergente, Chupeta, Removedor
- **Homens (M):** Presunto Cozido, Banana, Refrigerante, Preservativo, Bife de Coxão Mole

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

---

## 📝 Notas sobre os dados

### 🏷️ Produto sem cadastro

Todos os valores `#N/D` (3.650 registros, 0,44%) pertenciam a um único produto (`PR_ID = 107`), que não tinha nome nem categoria registrados.

- **Decisão:** preencher com `"Sem Categoria"` para preservar os registros.
- **Recomendação:** completar o cadastro do produto 107 na base de origem.

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