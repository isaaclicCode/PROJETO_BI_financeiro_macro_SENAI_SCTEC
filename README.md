# 📊  Financeiro — Macroeconomia, Taxas de Juros & Indicadores Econômicos

Projeto Avaliativo Final — Análise de dados públicos do BACEN (SGS) no período 2019–2023.

### 🔗 Links OficiaisBI
* **Trello (Kanban):** [preencher]
* **Streamlit Cloud:** [preencher]
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

---

## 🔬 Análise Exploratória de Dados (EDA)
A etapa de EDA foi documentada no notebook `notebooks/eda.ipynb`, consumindo diretamente a base consolidada (`macro_consolidado.csv`). Foram realizadas as seguintes análises:

1. **Estatísticas Descritivas:** Mapeamento de médias, medianas, desvios-padrão e valores extremos (mínimos e máximos) das variáveis econômicas. Destaca-se o registro de Juro Real negativo durante o período pandêmico.
2. **Matriz de Correlação de Pearson:** Heatmap interativo correlacionando todas as variáveis. Identificou-se forte correlação positiva entre o IPCA e a Selic (mecanismo de transmissão da política monetária) e correlação negativa entre o Dólar e o IBC-Br.
3. **Análise de Séries Temporais:** Plotagem de linhas do tempo (2019-2023) evidenciando o ciclo de aperto monetário pós-pandemia (alta da Selic), o pico inflacionário e a volatilidade cambial.
4. **Análise de Sazonalidade:** Agrupamento por mês (`mes`) para identificar padrões históricos. O IPCA apresenta picos sazonais em meses específicos (ex: início do ano), enquanto o IBC-Br mostra o comportamento da atividade econômica mês a mês.

### 💡 Principais Insights Obtidos (Resumo Executivo)
Com base na Análise Exploratória de Dados (EDA), destacam-se os seguintes achados para o período de 2019 a 2023:

1. **Ciclo de Juros e Juro Real:** O Juro Real Ex-Post foi negativo durante o ápice da pandemia (2020-2021), estimulando a economia. Contudo, com a escalada inflacionária, o Banco Central promoveu um forte aperto monetário, levando o Juro Real ao pico histórico de **10% em junho de 2023**.
2. **Comportamento Cambial:** O Dólar PTAX iniciou o período a R$ 3,75 e sofreu forte choque em 2020, mantendo-se acima da média do quinquênio (R$ 4,93) na maior parte do tempo.
3. **Inflação Importada (Choque Cambial):** Identificou-se uma correlação moderada (**0,477**) entre a desvalorização do Dólar e a alta do IPCA com defasagem de 3 meses, comprovando o repasse cambial para os preços domésticos.
4. **Freio na Atividade Econômica:** O IBC-Br mostrou forte recuperação em 2021, mas estagnou à medida que o ciclo de alta da Selic avançou, demonstrando o efeito da política monetária contracionista sobre o crescimento.
5. **Matriz de Correlação:** A matriz de Pearson evidenciou a forte interdependência entre a Selic e o Juro Real (0,78) e confirmou a correlação negativa entre o Juro Real e o IPCA Mensal (-0,40), validando o mecanismo de transmissão da política monetária.

> **⚠️ Limitações Metodológicas:** As análises de correlação não estabelecem causalidade. Além disso, o recorte temporal (2019-2023) engloba eventos atípicos (pandemia, choques geopolíticos), limitando a generalização dos padrões encontrados.git add README.md
git commit -m "docs: adiciona resumo executivo com os principais insights da EDA no README"

---

## 🗄️ Arquitetura de Banco de Dados (Cloud PostgreSQL)
Para garantir a resiliência e a escalabilidade do Data App, a base de dados consolidada foi migrada para um banco de dados relacional na nuvem, utilizando o **PostgreSQL** (hospedado no **Supabase**).

*   **Carga de Dados (`src/carga_sql.py`):** Script Python responsável por ler a base local (`macro_consolidado.csv`), tipar corretamente os dados (convertendo strings para `DATE` e `FLOAT`) e enviar via SQLAlchemy para a nuvem.
*   **Segurança e Credenciais:** As credenciais de acesso ao banco foram isoladas no arquivo `.streamlit/secrets.toml` (protegido pelo `.gitignore`), garantindo que nenhuma senha seja exposta no repositório público.
*   **Tabela em Nuvem:** A tabela `macro_consolidado` reside no schema `public` do Supabase, pronta para ser consumida via consultas SQL nativas pelo Data App.

---

## 🖥️ Data App (Streamlit)
A interface final do projeto foi construída utilizando o **Streamlit**, proporcionando uma experiência interativa e executiva para o usuário.

*   **Conexão Híbrida (Resiliência):** O app consome os dados diretamente do PostgreSQL (Supabase). Caso haja falha na nuvem, ele possui um `try/except` que ativa um *fallback* automático para o arquivo `.csv` local.
*   **Performance:** Uso de `@st.cache_data` (TTL de 1 hora) para evitar consultas desnecessárias ao banco.
*   **Filtros Dinâmicos:** Barra lateral com filtros por período (`date_input`), ano (`multiselect`) e botão de resetar filtros, utilizando `st.session_state` para persistência de navegação.
*   **KPIs Executivos:** Cartões de métricas (`st.metric`) para Selic, IPCA 12m, Dólar PTAX e Juro Real, incluindo comparação com o mês anterior (deltas).
*   **Visualizações Analíticas (Plotly Express):**
    *   *Política Monetária:* Gráfico combinado de linhas (Selic e IPCA) e barras (Juro Real).
    *   *Câmbio:* Linha do Dólar PTAX com marcação da média histórica.
    *   *Inflação:* Gráfico de dispersão relacionando Dólar e IPCA, colorido por ano e dimensionado pela Selic.
    *   *Atividade:* Linha do IBC-Br dessazonalizado.
    *   *Correlação:* Heatmap de Pearson com anotações numéricas.
*   **UX/UI (Pirâmide Invertida):** Estrutura organizada em abas que apresentam Contexto, Insight e Ação (metodologia Nielsen) no topo de cada tela para reduzir a carga cognitiva.
*   **Exportação:** Botão `st.download_button` para baixar os dados filtrados em CSV.

## 🎨 Interface e Design (UX/UI)

O Data App foi construído com foco em uma experiência de usuário executiva, limpa e de alta performance, seguindo as diretrizes da **Pirâmide Invertida (Contexto ➔ Insight ➔ Ação)** e as Heurísticas de Nielsen.

- **Identidade Visual Institucional (Estilo Gov.br):** O tema do Streamlit foi customizado (`.streamlit/config.toml`) utilizando as cores da bandeira do Brasil (Azul Bandeira, Verde Bandeira e Amarelo), transmitindo autoridade e confiança para o ambiente financeiro.
- **Cabeçalho Customizado:** Injeção de HTML/CSS para criar uma barra superior com a identidade visual do painel (BACEN | Macroeconomia).
- **Aviso Legal (Compliance e Ética):** Inclusão de um rodapé e alerta na *sidebar* deixando explícito que o projeto é estritamente acadêmico, sem vínculos oficiais com o Governo Federal, respeitando as diretrizes de Ética em Dados.
- **Navegação Fluida:** Interface organizada em 5 abas temáticas (`st.tabs`) para evitar a sobrecarga cognitiva e facilitar a navegação entre Política Monetária, Câmbio, Inflação, Atividade e Correlação.
- **Reatividade e Estado:** Filtros dinâmicos cruzados na barra lateral (`st.sidebar`) com botão de *Reset* funcional, gerenciados via `st.session_state`.
- **Exportação:** Botão para download da base filtrada em CSV (`st.download_button`), permitindo que o usuário final realize análises externas.

## 🚀 Como Executar o Projeto (Reprodutibilidade)
Para rodar o pipeline e o Data App localmente, siga os passos abaixo:

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
# Crie o arquivo .streamlit/secrets.toml com as credenciais do seu Supabase (modelo no secrets.toml.example)

# 7. Execute a carga para o PostgreSQL (Supabase)
python src/carga_sql.py

# 8. Inicie o Data App (Streamlit)
python -m streamlit run app.py
# O app abrirá automaticamente no seu navegador (http://localhost:8501)

## 🗂️ Estrutura do Repositório

├── data/                  # Base de dados bruta e tratada
│   ├── raw/               # Dados originais extraídos do BACEN
│   └── processed/         # Base consolidada pronta para uso (macro_consolidado.csv)
├── docs/logs/             # Relatórios de auditoria e transformação
├── notebooks/             # Análises exploratórias preliminares (EDA)
│   └── eda.ipynb          # Notebook com análises estatísticas e gráficos
├── src/                   # Scripts Python modulares
│   ├── etl_bacen.py       # Script de extração da API do BACEN
│   ├── tratamento.py      # Script de limpeza e cálculo de indicadores (Fórmula de Fisher)
│   └── carga_sql.py       # Script de envio da base consolidada para o Supabase (PostgreSQL)
├── .streamlit/            # Configurações de tema e modelo de credenciais
├── app.py                 # Código principal da aplicação Streamlit (Data App)
├── requirements.txt       # Bibliotecas e dependências para deploy na nuvem
├── .gitignore             # Arquivos ignorados pelo git (venv, secrets.toml, caches)
└── README.md              # Documentação oficial e completa do projeto

## ⚙️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Manipulação de Dados:** Pandas, NumPy
* **Requisições API:** Requests
* **Visualização de Dados:** Plotly Express, Seaborn, Matplotlib (EDA)
* **Banco de Dados & ORM:** PostgreSQL (Supabase), SQLAlchemy, Psycopg2
* **Data App:** Streamlit
* **Nuvem & Deploy:** Streamlit Community Cloud
* **Versionamento:** Git & GitFlow (GitHub)