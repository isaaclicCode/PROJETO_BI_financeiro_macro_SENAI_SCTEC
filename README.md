# 📊 BI Financeiro — Macroeconomia, Taxas de Juros & Indicadores Econômicos

Projeto Avaliativo Final — Análise de dados públicos do BACEN (SGS) no período 2019–2023.

## 🔗 Links Oficiais
- **Trello (Kanban):** _preencher_
- **Streamlit Cloud:** _preencher_
- **Vídeo Pitch:** _preencher_

## 🎯 Perguntas de Negócio
1. Evolução da Selic e Juro Real Ex-Post 2019–2023.
2. Trajetória do Dólar PTAX vs. média histórica do quinquênio.
3. Correlação entre choques cambiais (desvalorização do Real) e o avanço do IPCA.
4. Reação do IBC-Br aos ciclos de aperto e corte da Selic.
5. Matriz de correlação de Pearson entre as variáveis macroeconômicas.

## 📊 Fonte de Dados
- **Origem:** API pública oficial do Sistema Gerenciador de Séries Temporais (SGS) do Banco Central do Brasil (BACEN).
- **Endpoints Utilizados:**
  - `432`: Selic Meta (% a.a.)
  - `433`: IPCA Mensal (%)
  - `13522`: IPCA Acumulado 12 meses (%)
  - `1`: Dólar PTAX Venda (R$)
  - `24364`: IBC-Br Dessazonalizado (Índice de Atividade)
- **Período Temporal:** 01/01/2019 a 31/12/2023 (5 anos).

---

## ⚙️ Pipeline de ETL (Extração, Transformação e Carga)

O pipeline foi construído de forma modular e 100% reprodutível, utilizando **caminhos relativos** via `pathlib.Path` para garantir a execução em qualquer máquina e no Streamlit Cloud.

### 1. Extração (`src/etl_bacen.py`)
- **Processo:** O script consome a API do BACEN via biblioteca `requests`, extrai os dados brutos das 5 séries oficiais no formato JSON e os converte para arquivos `.csv` padronizados (`utf-8`).
- **Armazenamento:** Os dados brutos são salvos na pasta `data/raw/` (ex: `meta_selic_raw.csv`, `dolar_ptax_raw.csv`).

### 2. Tratamento e Consolidação (`src/tratamento.py`)
- **Higienização:** Tratamento de valores nulos, remoção de duplicatas (mantendo a última publicação em caso de retificação do BACEN) e padronização de encoding.
- **Conversão de Tipos:** Datas convertidas para `datetime` (padrão ISO) e strings numéricas convertidas para `float` (tratando vírgulas decimais pt-BR e pontos en-US).
- **Padronização Mensal:** Séries diárias (Selic e Dólar) são agregadas para base mensal (`MS` - Month Start). A Selic usa o último valor do mês (`.last()`) e o Dólar a média do mês (`.mean()`).
- **Cálculo Financeiro (Fórmula de Fisher):** Cálculo do **Juro Real Ex-Post** mensal para cada período, utilizando a equação exata:
  `Juro Real = ((1 + Selic/100) / (1 + IPCA_12m/100) - 1) * 100`
- **Saídas:**
  - `data/processed/macro_consolidado.csv`: Base final tratada (60 linhas × 10 colunas).
  - `docs/logs/transform_report.md`: Relatório de auditoria de qualidade (nulos, duplicatas e cobertura temporal).

### 3. Dicionário de Dados (Base Consolidada)
| Campo | Tipo | Descrição / Regra de Negócio |
| :--- | :--- | :--- |
| `data` | Datetime | Primeiro dia do mês de referência (formato YYYY-MM-DD). |
| `selic_meta` | Float | Taxa Selic Meta vigente no fim do mês (% a.a.). |
| `ipca_mensal` | Float | Variação percentual do IPCA no mês (%). |
| `ipca_12m` | Float | IPCA acumulado nos últimos 12 meses (%). |
| `dolar_ptax` | Float | Taxa de câmbio Dólar PTAX Venda (média dos dias úteis do mês). |
| `ibc_br` | Float | Índice de Atividade Econômica do Banco Central (dessazonalizado). |
| `juro_real` | Float | Juro Real Ex-Post calculado via Fórmula de Fisher (% a.a.). |
| `ano` | Int | Ano extraído da data (2019 a 2023). |
| `mes` | Int | Mês extraído da data (1 a 12). |
| `trimestre` | Int | Trimestre extraído da data (1 a 4). |

## 🚀 Como Executar o Projeto (Reprodutibilidade)

Para rodar o pipeline localmente, siga os passos abaixo:

```bash
# 1. Clone o repositório e acesse a pasta
git clone https://github.com/SEU_USUARIO/bi-financeiro-macro.git
cd bi-financeiro-macro

# 2. Crie e ative o ambiente virtual
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a extração (gera os arquivos em data/raw/)
python src/etl_bacen.py

# 5. Execute o tratamento (gera a base consolidada em data/processed/)
python src/tratamento.py

# 6. Inicie o Data App (Streamlit)
streamlit run app.py

## 🗂️ Estrutura

├── data/                  # Base de dados bruta e tratada (ou script/instruções para download)
├── notebooks/             # Análises exploratórias preliminares (EDA) e prototipagem de cálculos
├── src/                   # Scripts Python modulares (ETL, funções de cálculo de indicadores financeiros)
├── .streamlit/            # Configurações de tema (config.toml) e modelo de credenciais (secrets.toml.example)
├── app.py                 # Código principal da aplicação Streamlit (Data App)
├── requirements.txt       # Bibliotecas e dependências para deploy na nuvem
├── .gitignore             # Arquivos ignorados pelo Git (venv, secrets.toml, caches)
└── README.md              # Documentação oficial e completa do projeto

⚙️ Tecnologias Utilizadas

Linguagem: Python 3.x
Manipulação de Dados: Pandas, NumPy
Requisições API: Requests
Visualização: Plotly Express
Data App: Streamlit
Banco de Dados / Nuvem: PostgreSQL (Supabase) + Streamlit Community Cloud
Versionamento: Git & GitFlow (GitHub)

