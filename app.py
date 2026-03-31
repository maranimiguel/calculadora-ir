import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# 1. Configuração e Estilo
st.set_page_config(page_title="Dashboard IRRF 2026 Pro", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { color: #2E7D32; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CÁLCULO CENTRALIZADA ---
def calcular_completo(sal_bruto, n_dep):
    # INSS 2026
    if sal_bruto <= 1621.00: inss = round(sal_bruto * 0.075, 2)
    elif sal_bruto <= 2902.84: inss = round((sal_bruto * 0.09) - 24.32, 2)
    elif sal_bruto <= 4354.27: inss = round((sal_bruto * 0.12) - 111.40, 2)
    else:
        v_base_inss = min(sal_bruto, 8475.55)
        inss = round((v_base_inss * 0.14) - 198.49, 2)
    
    # Deduções
    d_dep = round(n_dep * 189.59, 2)
    d_simp = 607.20
    m_deducao = max(inss + d_dep, d_simp)
    base_ir = round(max(0.0, sal_bruto - m_deducao), 2)

    # IRRF Tabela 2026
    if base_ir <= 2428.80: ir_b = 0.0
    elif base_ir <= 2826.65: ir_b = (base_ir * 0.075) - 182.16
    elif base_ir <= 3751.05: ir_b = (base_ir * 0.15) - 394.16
    elif base_ir <= 4664.68: ir_b = (base_ir * 0.225) - 675.49
    else: ir_b = (base_ir * 0.275) - 908.73
    ir_b = round(max(0.0, ir_b), 2)

    # Redutor Especial 2026 (SECOM)
    red = 0.0
    if 5000.00 < sal_bruto <= 7350.00:
        red = round(978.62 - (0.133145 * sal_bruto), 2)
    elif sal_bruto <= 5000.00:
        red = ir_b
    
    ir_f = round(max(0.0, ir_b - red), 2)
    return inss, ir_f, round(sal_bruto - inss - ir_f, 2), red, m_deducao == d_simp

# --- INTERFACE ---
st.title("📊 Planejamento Tributário 2026")

tab_calc, tab_grafico = st.tabs(["💵 Calculadora Personalizada", "📈 Curva de Impostos (Análise de Sensibilidade)"])

with st.sidebar:
    st.header("⚙️ Parâmetros")
    s_bruto = st.number_input("Salário Bruto Atual (R$):", min_value=0.0, value=5001.0, step=100.0)
    deps = st.number_input("Dependentes:", min_value=0, value=0)
    
    st.divider()
    st.header("🔍 Limites do Gráfico")
    # Widget de Range para os limites do gráfico
    limite_inf, limite_sup = st.slider(
        "Selecione o intervalo de salário para o gráfico:",
        min_value=0, 
        max_value=100000, 
        value=(0, 20000), # Valor padrão inicial focado na classe média
        step=500
    )

# CÁLCULO PRINCIPAL
v_inss, v_irrf, v_liquido, v_redutor, is_simp = calcular_completo(s_bruto, deps)
v_total_imp = round(v_inss + v_irrf, 2)
v_aliq_efet = round((v_total_imp / s_bruto) * 100, 2) if s_bruto > 0 else 0

# --- ABA 1: CALCULADORA ---
with tab_calc:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Líquido Mensal", f"R$ {v_liquido:,.2f}")
    c2.metric("Total Impostos", f"R$ {v_total_imp:,.2f}", f"{v_aliq_efet}%", delta_color="inverse")
    c3.metric("Bônus Redutor", f"R$ {v_redutor:,.2f}")
    c4.metric("Modelo Aplicado", "Simplificado" if is_simp else "Deduções")

    st.divider()
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Líquido', 'INSS', 'IRRF'],
            values=[v_liquido, v_inss, v_irrf],
            hole=.5, marker=dict(colors=['#2ecc71', '#e74c3c', '#f1c40f'])
        )])
        fig_donut.update_layout(title="Distribuição Percentual do Salário Selecionado")
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_r:
        st.subheader("📝 Resumo")
        res_df = pd.DataFrame({"Descrição": ["Bruto", "INSS", "IRRF", "Líquido"], 
                                "Valor": [s_bruto, v_inss, v_irrf, v_liquido]})
        st.table(res_df.set_index("Descrição"))

# --- ABA 2: GRÁFICO DE SENSIBILIDADE COM LIMITES DINÂMICOS ---
with tab_grafico:
    st.subheader(f"Evolução da Carga Tributária: R$ {limite_inf} a R$ {limite_sup}")
    
    # Gerar dados baseados nos limites escolhidos pelo usuário
    faixas = np.linspace(limite_inf, limite_sup, 200)
    dados_list = [calcular_completo(f, deps) for f in faixas]
    
    df_curva = pd.DataFrame(dados_list, columns=['INSS', 'IRRF', 'Liquido', 'Redutor', 'IsSimp'])
    df_curva['Bruto'] = faixas

    # Gráfico de Áreas Empilhadas
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=df_curva['Bruto'], y=df_curva['Liquido'], name='Líquido', stackgroup='one', line=dict(color='#2ecc71')))
    fig_curva.add_trace(go.Scatter(x=df_curva['Bruto'], y=df_curva['INSS'], name='INSS', stackgroup='one', line=dict(color='#e74c3c')))
    fig_curva.add_trace(go.Scatter(x=df_curva['Bruto'], y=df_curva['IRRF'], name='IRRF', stackgroup='one', line=dict(color='#f1c40f')))

    fig_curva.update_layout(
        xaxis_title="Salário Bruto (R$)",
        yaxis_title="Composição (R$)",
        hovermode="x",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    st.plotly_chart(fig_curva, use_container_width=True)
    
    st.info(f"O gráfico acima está filtrado para o intervalo de **R$ {limite_inf:,.2f}** a **R$ {limite_sup:,.2f}**.")
