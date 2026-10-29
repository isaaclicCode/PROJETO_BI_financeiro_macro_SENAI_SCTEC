# 📊 BI Financeiro — Macroeconomia, Taxas de Juros & Indicadores Econômicos

Projeto Avaliativo Final — Análise de dados públicos do BACEN (SGS) no período 2019–2023.

### 🔗 Links Oficiais
* **GitHub (Gitflow):** https://github.com/isaaclicCode/PROJETO_BI_financeiro_macro_SENAI_SCTEC/tree/main
* **Trello (Kanban):** https://trello.com/invite/b/6ad4d206a7b4284207a118ba/ATTI03c7af5523dfc2c8ec6bd7610a97ef8fA4F15AD5/visualizacao-de-dados-e-bi-macroeconomia-taxas-de-juros-indicadores-economicos-banco-central-ipea
* **Streamlit Cloud:** https://projetofinalbifinanceiromacroeconomicosctec.streamlit.app/
* **Vídeo Pitch:** [preencher]

---

## 🎯 Perguntas de Negócio
1. Evolução da Selic e Juro Real Ex-Post 2019–2023.
2. Trajetória do Dólar PTAX vs. média histórica do quinquênio.
3. Correlação entre choques cambiais (desvalorização do Real) e o avanço do IPCA.
4. Reação do IBC-Br aos ciclos de aperto e corte da Selic.
5. Matriz de correlação de Pearson entre as variáveis macroeconômicas.

---

## 📊 Fonte de Dados
* **Origem:** API pública oficial do Sistema Gerenciador de Séries Temporais (SGS) do Banco Central do Brasil (BACEN).
* **Endpoints Utilizados:**
  * `432`: Selic Meta (% a.a.)
  * `433`: IPCA Mensal (%)
  * `13522`: IPCA Acumulado 12 meses (%)
  * `1`: Dólar PTAX Venda (R$)
  * `24364`: IBC-Br Dessazonalizado (Índice de Atividade)
* **Período Temporal:** 01/01/2019 a 31/12/2023 (5 anos).

---

## ⚙️ Pipeline de ETL (Extração, Transformação e Carga)
O pipeline foi construído de forma modular e 100% reprodutível, utilizando caminhos relativos via `pathlib.Path` para garantir a execução em qualquer máquina e no Streamlit Cloud.

### 1. Extração (`src/etl_bacen.py`)
* **Processo:** O script consome a API do BACEN via biblioteca `requests`, extrai os dados brutos das 5 séries oficiais no formato JSON e os converte para arquivos `.csv` padronizados (utf-8).
* **Armazenamento:** Os dados brutos são salvos na pasta `data/raw/`.

### 2. Tratamento e Consolidação (`src/tratamento.py`)
* **Higienização:** Tratamento de valores nulos, remoção de duplicatas e padronização de encoding.
* **Conversão de Tipos:** Datas convertidas para `datetime` e strings numéricas convertidas para `float`.
* **Padronização Mensal:** Séries diárias (Selic e Dólar) são agregadas para base mensal (MS - Month Start).
* **Cálculo Financeiro (Fórmula de Fisher):** Cálculo do Juro Real Ex-Post mensal: `Juro Real = ((1 + Selic/100) / (1 + IPCA_12m/100) - 1) * 100`.
* **Saídas:** 
  * `data/processed/macro_consolidado.csv`: Base final tratada (60 linhas × 10 colunas).
  * `docs/logs/transform_report.md`: Relatório de auditoria de qualidade.

---

## 📖 Dicionário de Dados (Base Consolidada)
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

---

## 🔬 Análise Exploratória de Dados (EDA)
A etapa de EDA foi documentada no notebook `notebooks/eda.ipynb`, consumindo diretamente a base consolidada (`macro_consolidado.csv`). Foram realizadas as seguintes análises:

1. **Estatísticas Descritivas:** Mapeamento de médias, medianas, desvios-padrão e valores extremos das variáveis econômicas. Destaca-se o registro de Juro Real negativo durante o período pandêmico.
2. **Matriz de Correlação de Pearson:** Heatmap interativo correlacionando todas as variáveis. Identificou-se forte correlação positiva entre o IPCA e a Selic e correlação negativa entre o Dólar e o IBC-Br.
3. **Análise de Séries Temporais:** Plotagem de linhas do tempo (2019-2023) evidenciando o ciclo de aperto monetário pós-pandemia (alta da Selic), o pico inflacionário e a volatilidade cambial.
4. **Análise de Sazonalidade:** Agrupamento por mês para identificar padrões históricos. O IPCA apresenta picos sazonais em meses específicos, enquanto o IBC-Br mostra o comportamento da atividade econômica mês a mês.

### 💡 Principais Insights Obtidos (Resumo Executivo)
1. **Ciclo de Juros e Juro Real:** O Juro Real Ex-Post foi negativo durante o ápice da pandemia (2020-2021), estimulando a economia. Contudo, com a escalada inflacionária, o Banco Central promoveu um forte aperto monetário, levando o Juro Real ao pico histórico de **10% em junho de 2023**.
2. **Comportamento Cambial:** O Dólar PTAX iniciou o período a R$ 3,75 e sofreu forte choque em 2020, mantendo-se acima da média do quinquênio (R$ 4,93) na maior parte do tempo.
3. **Inflação Importada (Choque Cambial):** Identificou-se uma correlação moderada (**0,477**) entre a desvalorização do Dólar e a alta do IPCA com defasagem de 3 meses, comprovando o repasse cambial para os preços domésticos.
4. **Freio na Atividade Econômica:** O IBC-Br mostrou forte recuperação em 2021, mas estagnou à medida que o ciclo de alta da Selic avançou, demonstrando o efeito da política monetária contracionista sobre o crescimento.
5. **Matriz de Correlação:** A matriz de Pearson evidenciou a forte interdependência entre a Selic e o Juro Real (0,78) e confirmou a correlação negativa entre o Juro Real e o IPCA Mensal (-0,40).

> **⚠️ Limitações Metodológicas:** As análises de correlação não estabelecem causalidade. Além disso, o recorte temporal (2019-2023) engloba eventos atípicos (pandemia, choques geopolíticos), limitando a generalização dos padrões encontrados.

---

## 🗄️ Arquitetura de Banco de Dados (Cloud PostgreSQL)
Para garantir a resiliência e a escalabilidade do Data App, a base de dados consolidada foi migrada para um banco de dados relacional na nuvem, utilizando o **PostgreSQL** (hospedado no **Supabase**).

* **Carga de Dados (`src/carga_sql.py`):** Script Python responsável por ler a base local, tipar corretamente os dados e enviar via SQLAlchemy para a nuvem.
* **Segurança e Credenciais:** As credenciais de acesso foram isoladas no arquivo `.streamlit/secrets.toml` (protegido pelo `.gitignore`).
* **Tabela em Nuvem:** A tabela `macro_consolidado` reside no schema `public` do Supabase, pronta para ser consumida via consultas SQL nativas pelo Data App.

---

## 🖥️ Data App (Streamlit)
A interface final do projeto foi construída utilizando o **Streamlit**, proporcionando uma experiência interativa e executiva.

* **Conexão Híbrida (Resiliência):** O app consome dados do PostgreSQL. Caso haja falha, um `try/except` ativa um *fallback* automático para o arquivo `.csv` local.
* **Performance:** Uso de `@st.cache_data` (TTL de 1 hora) para evitar consultas desnecessárias ao banco.
* **Filtros Dinâmicos:** Barra lateral com filtros por período, ano e botão de resetar filtros, utilizando `st.session_state`.
* **KPIs Executivos:** Cartões de métricas (`st.metric`) para Selic, IPCA 12m, Dólar PTAX e Juro Real, com comparação de deltas.
* **Visualizações Analíticas (Plotly Express):**
  * *Política Monetária:* Gráfico combinado de linhas (Selic e IPCA) e barras (Juro Real).
  * *Câmbio:* Linha do Dólar PTAX com marcação da média histórica.
  * *Inflação:* Gráfico de dispersão relacionando Dólar e IPCA, colorido por ano e dimensionado pela Selic.
  * *Atividade:* Linha do IBC-Br dessazonalizado.
  * *Correlação:* Heatmap de Pearson com anotações numéricas.
* **Exportação:** Botão `st.download_button` para baixar os dados filtrados em CSV.

### 🎨 Interface e Design (UX/UI)
O Data App foi construído com foco em uma experiência de usuário executiva, limpa e de alta performance, seguindo as diretrizes da **Pirâmide Invertida (Contexto ➔ Insight ➔ Ação)** e as Heurísticas de Nielsen.

* **Identidade Visual Institucional (Estilo Gov.br):** O tema foi customizado (`.streamlit/config.toml`) utilizando as cores da bandeira do Brasil.
* **Cabeçalho Customizado:** Injeção de HTML/CSS para criar uma barra superior com a identidade visual do painel.
* **Aviso Legal (Compliance e Ética):** Inclusão de um rodapé e alerta na *sidebar* deixando explícito que o projeto é estritamente acadêmico, sem vínculos oficiais com o Governo Federal.
* **Navegação Fluida:** Interface organizada em 5 abas temáticas (`st.tabs`) para evitar a sobrecarga cognitiva.

---

## 🚀 Como Executar o Projeto (Reprodutibilidade)
Para rodar o pipeline e o Data App localmente, siga os passos abaixo:

```bash
# 1. Clone o repositório e acesse a pasta
git clone https://github.com/isaaclicCode/PROJETO_BI_financeiro_macro_SENAI_SCTEC.git
cd PROJETO_BI_financeiro_macro_SENAI_SCTEC

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

# 6. Configure as credenciais do banco
# Crie o arquivo .streamlit/secrets.toml com as credenciais do seu Supabase

# 7. Execute a carga para o PostgreSQL (Supabase)
python src/carga_sql.py

# 8. Inicie o Data App (Streamlit)
python -m streamlit run app.py

## 🗂️ Estrutura do Repositório

```text
PROJETO_BI_financeiro_macro_SENAI_SCTEC/
├── .streamlit/                    # Configurações do Streamlit
│   ├── config.toml                # Customização do tema (Cores Gov.br)
│   ├── secrets.toml               # Credenciais locais (Ignorado pelo Git)
│   └── secrets.toml.example       # Modelo de exemplo para credenciais
├── data/                          # Diretório de dados
│   ├── processed/                 # Dados limpos e consolidados
│   │   ├── dolar_ptax_processed.csv
│   │   ├── ibc_br_processed.csv
│   │   ├── ipca_12m_processed.csv
│   │   ├── ipca_mensal_processed.csv
│   │   ├── macro_consolidado.csv  # Base final utilizada no App
│   │   └── meta_selic_processed.csv
│   └── raw/                       # Dados brutos extraídos da API
│       ├── dolar_ptax_raw.csv
│       ├── ibc_br_raw.csv
│       ├── ipca_12m_raw.csv
│       ├── ipca_mensal_raw.csv
│       └── meta_selic_raw.csv
├── docs/                          
│   └── logs/                      # Relatórios de auditoria
│       └── transform_report.md    # Log gerado pelo script de tratamento
├── notebooks/                     # Análises exploratórias
│   └── eda.ipynb                  # Notebook com a Análise Exploratória (EDA)
├── src/                           # Scripts Python (Pipeline ETL e Carga)
│   ├── carga_sql.py               # Script de envio para o PostgreSQL (Supabase)
│   ├── etl_bacen.py               # Script de extração da API do BACEN
│   └── tratamento.py              # Script de limpeza, merge e Fórmula de Fisher
├── venv/                          # Ambiente virtual (Ignorado pelo Git)
├── .gitignore                     # Arquivos ignorados pelo Git
├── app.py                         # Código principal do Data App Streamlit
├── README.md                      # Documentação oficial do projeto
└── requirements.txt               # Dependências do projeto para deploy


⚙️ Tecnologias Utilizadas

Linguagem: Python 3.x

Manipulação de Dados: Pandas, NumPy

Requisições API: Requests

Visualização de Dados: Plotly Express, Seaborn, Matplotlib (EDA)

Banco de Dados & ORM: PostgreSQL (Supabase), SQLAlchemy, Psycopg2

Data App: Streamlit

Nuvem & Deploy: Streamlit Community Cloud

Versionamento: Git & GitFlow (GitHub)