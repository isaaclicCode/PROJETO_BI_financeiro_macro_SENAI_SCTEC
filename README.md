cat > README.md << 'EOF'
# 📊 BI Financeiro — Macroeconomia, Taxas de Juros & Indicadores Econômicos

Projeto Avaliativo Final — Análise de dados públicos do BACEN (SGS) no período 2019–2023.

## 🔗 Links Oficiais
- **Trello (Kanban):** _preencher_
- **Streamlit Cloud:** _preencher_
- **Vídeo Pitch:** _preencher_

## 🎯 Perguntas de Negócio
1. Evolução da Selic e Juro Real Ex-Post 2019–2023
2. Trajetória do Dólar PTAX vs. média histórica
3. Correlação choques cambiais × IPCA
4. Reação do IBC-Br aos ciclos de Selic
5. Matriz de correlação de Pearson

## 📊 Fonte de Dados
- API SGS/BACEN — Séries 432, 433, 13522, 1, 24364
- Período: 01/01/2019 a 31/12/2023

## ⚙️ Tecnologias
Python · Pandas · Plotly · Streamlit · PostgreSQL (Supabase) · GitFlow

## 🗂️ Estrutura

├── data/                  # Base de dados bruta e tratada (ou script/instruções para download)
├── notebooks/             # Análises exploratórias preliminares (EDA) e prototipagem de cálculos
├── src/                   # Scripts Python modulares (ETL, funções de cálculo de indicadores financeiros)
├── .streamlit/            # Configurações de tema (config.toml) e modelo de credenciais (secrets.toml.example)
├── app.py                 # Código principal da aplicação Streamlit (Data App)
├── requirements.txt       # Bibliotecas e dependências para deploy na nuvem
├── .gitignore             # Arquivos ignorados pelo Git (venv, secrets.toml, caches)
└── README.md              # Documentação oficial e completa do projeto