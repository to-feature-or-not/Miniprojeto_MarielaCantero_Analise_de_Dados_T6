# Mini Desafio Semana 7 — Análise de Vendas do Setor Varejista

Análise exploratória de dados de vendas de uma rede de supermercados, com foco em sazonalidade, comportamento de compra e perfil do cliente.

**Curso:** SCTEC — Etapa Profissionalizar
**Autor:** [to-feature-or-not](https://github.com/to-feature-or-not)
**Data:** 2026-09-10

---

## 📋 Sobre o projeto

Este projeto realiza uma análise completa de um dataset com **830.000 registros** de vendas do setor varejista, cobrindo o período de **2019 a 2022**.

O pipeline inclui:

- Limpeza e tratamento de dados faltantes
- Conversão e validação de datas
- Detecção e agrupamento de duplicatas
- Análises de sazonalidade, produtos, categorias e clientes
- Geração de gráficos e relatórios

---

## 📁 Estrutura do projeto

```
Miniprojeto_MarielaCantero_Analise_de_Dados_T6
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
- **seaborn** — heatmap de sazonalidade

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



## 👤 Autor

**Mariela Cantero** — [@to-feature-or-not](https://github.com/to-feature-or-not)
Mini-projeto avaliativo — Setembro/2026