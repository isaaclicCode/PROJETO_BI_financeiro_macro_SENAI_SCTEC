import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 22. SETUP DA APP STREAMLIT
# ==========================================
st.set_page_config(page_title="BI Financeiro Macro", layout="wide", page_icon="📊")

# --- CABEÇALHO INSTITUCIONAL (ESTILO GOV.BR) ---
st.markdown("""
    <style>
        /* Barra superior verde e amarela */
        .gov-header {
            background-color: #002776; /* Fundo Azul */
            padding: 15px;
            border-bottom: 5px solid #009c3b; /* Linha Verde */
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            color: white;
        }
        .gov-header h1 {
            color: white !important;
            font-size: 24px !important;
            margin: 0;
            padding: 0;
        }
        .gov-header span {
            color: #ffdf00; /* Amarelo Bandeira */
            font-weight: bold;
        }
    </style>
    <div class="gov-header">
        <h1>🇧🇷 <span>BACEN</span> | Painel Macroeconômico Institucional</h1>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 23 e 24. CONEXÃO RESILIENTE + CACHE
# ==========================================
@st.cache_data(ttl=3600)
def carregar_dados():
    try:
        # conexão ao Supabase
        conn = st.connection("postgresql", type="sql")
        df = conn.query("SELECT * FROM macro_consolidado", ttl=3600)
        return df, "Nuvem (Supabase PostgreSQL)"
    except Exception:
        # Fallback local (Contingência)
        BASE_DIR = Path(__file__).resolve().parent
        df = pd.read_csv(BASE_DIR / "data" / "processed" / "macro_consolidado.csv")
        return df, "Local (Fallback CSV)"

df, status_conexao = carregar_dados()
df['data'] = pd.to_datetime(df['data'])

# ==========================================
# 25. SIDEBAR COM FILTROS DINÂMICOS + SESSION STATE
# ==========================================
st.sidebar.header("Filtros Dinâmicos")
st.sidebar.success(f"Fonte: {status_conexao}")

data_min = df['data'].min().date()
data_max = df['data'].max().date()
anos_disponiveis = sorted(df['ano'].unique().tolist())

# Inicializando a Session State para os filtros
if "filtro_data_ini" not in st.session_state:
    st.session_state.filtro_data_ini = data_min
if "filtro_data_fim" not in st.session_state:
    st.session_state.filtro_data_fim = data_max
if "filtro_anos" not in st.session_state:
    st.session_state.filtro_anos = anos_disponiveis

# Função para resetar os filtros
def resetar_filtros():
    st.session_state.filtro_data_ini = data_min
    st.session_state.filtro_data_fim = data_max
    st.session_state.filtro_anos = anos_disponiveis

# Widgets da Sidebar
data_inicio = st.sidebar.date_input("Data Inicial", st.session_state.filtro_data_ini, min_value=data_min, max_value=data_max)
data_fim = st.sidebar.date_input("Data Final", st.session_state.filtro_data_fim, min_value=data_min, max_value=data_max)
anos_selecionados = st.sidebar.multiselect("Selecione os Anos", anos_disponiveis, default=st.session_state.filtro_anos)

st.sidebar.button("🔄 Resetar Filtros", on_click=resetar_filtros)

# Aplicando os filtros
df_filtrado = df[
    (df['data'].dt.date >= data_inicio) & 
    (df['data'].dt.date <= data_fim) & 
    (df['ano'].isin(anos_selecionados))
]

# Se o filtro deixar a base vazia, avisa o usuário
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados. Ajuste a barra lateral.")
    st.stop()

st.sidebar.markdown("---")
# CORREÇÃO AQUI: Fechamento do parênteses no st.sidebar.info
st.sidebar.info(
    "⚠️ **Aviso:** Este é um projeto acadêmico e de portfólio. "
    "Não possui vínculo oficial com o Governo Federal ou o BACEN."
)

# ==========================================
# ABAS TEMÁTICAS + UX/UI PIRÂMIDE INVERTIDA
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Visão Geral", "💵 Câmbio", "🔥 Inflação", "🏭 Atividade", "🧮 Correlação e Dados"
])

# --- ABA 1: VISÃO GERAL E KPIs ---
with tab1:
    st.markdown("### Contexto, Insight e Ação")
    st.info("**Contexto:** Acompanhamento do ciclo de política monetária no Brasil. **Insight:** A elevação da Selic buscou ancorar as expectativas de inflação. **Ação:** Monitorar o Juro Real para avaliar o custo de crédito.")
    
    # 4 KPIs com deltas comparativos (mês atual vs mês anterior)
    st.markdown("#### Resumo do Último Mês no Período")
    col1, col2, col3, col4 = st.columns(4)
    
    # Cálculo de variação (delta)
    def calc_delta(serie):
        if len(serie) >= 2:
            return f"{serie.iloc[-1] - serie.iloc[-2]:.2f} vs mês ant."
        return None

    with col1:
        st.metric("Selic Meta", f"{df_filtrado['selic_meta'].iloc[-1]:.2f}%", delta=calc_delta(df_filtrado['selic_meta']))
    with col2:
        st.metric("IPCA 12M", f"{df_filtrado['ipca_12m'].iloc[-1]:.2f}%", delta=calc_delta(df_filtrado['ipca_12m']), delta_color="inverse")
    with col3:
        st.metric("Juro Real Ex-Post", f"{df_filtrado['juro_real'].iloc[-1]:.2f}%", delta=calc_delta(df_filtrado['juro_real']))
    with col4:
        st.metric("Dólar PTAX", f"R$ {df_filtrado['dolar_ptax'].iloc[-1]:.2f}", delta=calc_delta(df_filtrado['dolar_ptax']), delta_color="inverse")

    # Gráfico 1 — Política Monetária (Linha + Linha + Barra)
    st.markdown("#### Política Monetária: Selic, IPCA e Juro Real")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=df_filtrado['data'], y=df_filtrado['juro_real'], name='Juro Real', marker_color='rgba(255, 165, 0, 0.5)'))
    fig1.add_trace(go.Scatter(x=df_filtrado['data'], y=df_filtrado['selic_meta'], mode='lines', name='Selic Meta', line=dict(color='blue', width=3)))
    fig1.add_trace(go.Scatter(x=df_filtrado['data'], y=df_filtrado['ipca_12m'], mode='lines', name='IPCA 12M', line=dict(color='red', width=2, dash='dash')))
    fig1.update_layout(title="Evolução dos Juros e Inflação", yaxis_title="Taxa (%)", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig1, use_container_width=True)

# --- ABA 2: CÂMBIO ---
with tab2:
    st.markdown("### Análise Cambial")
    st.info("**Contexto:** Trajetória do Dólar PTAX. **Insight:** O câmbio apresentou forte volatilidade, mantendo-se acima da média histórica no período recente. **Ação:** Avaliar impacto nos custos de importação.")
    
    # Gráfico 2 — Linha Cambial com Média
    media_dolar = df_filtrado['dolar_ptax'].mean()
    fig2 = px.line(df_filtrado, x='data', y='dolar_ptax', title="Cotação do Dólar PTAX vs Média Histórica")
    fig2.add_hline(y=media_dolar, line_dash="dash", line_color="red", annotation_text=f"Média: R$ {media_dolar:.2f}", annotation_position="bottom right")
    fig2.update_layout(yaxis_title="R$", xaxis_title="Data")
    st.plotly_chart(fig2, use_container_width=True)

# --- ABA 3: INFLAÇÃO ---
with tab3:
    st.markdown("### Repasse Cambial e Inflação")
    st.info("**Contexto:** Relação entre Dólar e IPCA. **Insight:** Observa-se correlação visual entre choques cambiais e a aceleração inflacionária. **Ação:** Utilizar modelos de hedge cambial.")
    
    # Gráfico 3 — Dispersão Macroeconômica
    fig3 = px.scatter(
        df_filtrado, x='dolar_ptax', y='ipca_12m', 
        color='ano', size='selic_meta', 
        title="Dispersão: Dólar x IPCA 12M (Cor=Ano, Tamanho=Selic)",
        labels={'dolar_ptax': 'Dólar PTAX (R$)', 'ipca_12m': 'IPCA 12M (%)', 'ano': 'Ano'}
    )
    st.plotly_chart(fig3, use_container_width=True)

# --- ABA 4: ATIVIDADE ---
with tab4:
    st.markdown("### Atividade Econômica")
    st.info("**Contexto:** Índice IBC-Br dessazonalizado. **Insight:** O crescimento econômico desacelerou após o ciclo de aperto monetário. **Ação:** Ajustar projeções de receita e PIB para o próximo trimestre.")
    
    # Gráfico 4 — IBC-Br
    fig4 = px.line(df_filtrado, x='data', y='ibc_br', title="Evolução do IBC-Br (Atividade Econômica)", markers=True)
    fig4.update_traces(line_color='purple', line_width=3)
    fig4.update_layout(yaxis_title="Índice", xaxis_title="Data")
    st.plotly_chart(fig4, use_container_width=True)

# --- ABA 5: CORRELAÇÃO E DADOS ---
with tab5:
    st.markdown("### Matriz de Correlação de Pearson")
    st.info("**Contexto:** Interdependência das variáveis. **Insight:** O Juro Real possui forte relação com a Selic e correlação negativa com o IPCA. **Ação:** Analisar cenários multivariados.")
    
    # Gráfico 5 — Heatmap de Pearson
    colunas_numericas = ['selic_meta', 'ipca_mensal', 'ipca_12m', 'dolar_ptax', 'ibc_br', 'juro_real']
    corr = df_filtrado[colunas_numericas].corr()
    
    fig5 = px.imshow(
        corr, text_auto=True, aspect="auto", 
        color_continuous_scale='RdBu_r', zmin=-1, zmax=1,
        title="Heatmap de Correlação"
    )
    st.plotly_chart(fig5, use_container_width=True)
    
    st.divider()
    
    # Exportação (Download Button)
    st.markdown("### Dados Filtrados e Exportação")
    st.dataframe(df_filtrado, use_container_width=True)
    
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Filtrados (CSV)",
        data=csv,
        file_name='dados_macro_filtrados.csv',
        mime='text/csv',
    )

# ==============================================================================
# RODAPÉ E AVISO LEGAL
# ==============================================================================
st.markdown("---")
st.markdown("""
    <div style="background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; border-left: 5px solid #ffc107; margin-top: 20px; font-size: 14px;">
        <strong>⚠️ Aviso Legal:</strong> Este aplicativo foi desenvolvido estritamente para fins <b>acadêmicos e educacionais</b> como parte de um Projeto Avaliativo. 
        Ele <b>não representa</b> informações oficiais, não possui vínculo com o Banco Central do Brasil (BACEN) ou qualquer órgão do Governo Federal. 
        Os dados são de fontes públicas oficiais (API SGS/BACEN), mas as análises, interfaces e interpretações aqui presentes são de inteira responsabilidade do autor do projeto.
    </div>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align: center; color: #666; font-size: 12px; margin-top: 20px;'>"
    "Desenvolvido por Isaac Trenard | Projeto SENAI SCTEC</p>", 
    unsafe_allow_html=True
)