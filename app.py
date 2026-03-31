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

# --- FUNÇÃO DE CÁLCULO CENTRALIZADA (Para evitar repetição) ---
def calcular_completo(sal_bruto, n_dep):
    # INSS
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

    # IRRF Tabela
    if base_ir <= 2428.80: ir_b = 0.0
    elif base_ir <= 2826.65: ir_b = (base_ir * 0.075) - 182.16
    elif base_ir <= 3751.05: ir_b = (base_ir * 0.15) - 394.16
    elif base_ir <= 4664.68: ir_b = (base_ir * 0.225) - 675.49
    else: ir_b = (base_ir * 0.275) - 908.73
    ir_b = round(max(0.0, ir_b), 2)

    # Redutor SECOM 2026
    red = 0.0
    if 5000.00 < sal_bruto <= 7350.00:
        red = round(978.62 - (0.133145 * sal_bruto), 2)
    elif sal_bruto <= 5000.00:
        red = ir_b
    
    ir_f = round(max(0.0, ir_b - red), 2)
    return inss, ir_f, round(sal_bruto - inss - ir_f, 2), red, m_deducao == d_simp

# --- INTERFACE ---
st.title("📊 Planejamento Tributário 2026")

# Abas do Sistema
tab_calc, tab_grafico = st.tabs(["💵 Calculadora Personalizada", "📈 Curva de Impostos (0 a 100k)"])

with st.sidebar:
    st.header("⚙️ Parâmetros")
    s_bruto = st.number_input("Salário Bruto (R$):", min_value=0.0, value=5001.0, step=100.0)
    deps = st.number_input("Dependentes:", min_value=0, value=0)

# EXECUÇÃO DO CÁLCULO PRINCIPAL
v_inss, v_irrf, v_liquido, v_redutor, is_simp = calcular_completo(s_bruto, deps)
v_total_imp = round(v_inss + v_irrf, 2)
v_aliq_efet = round((v_total_imp / s_bruto) * 100, 2) if s_bruto > 0 else 0

# --- CONTEÚDO DA ABA 1 ---
with tab_calc:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Líquido Mensal", f"R$ {v_liquido:,.2f}")
    c2.metric("Total Impostos", f"R$ {v_total_imp:,.2f}", f"{v_aliq_efet}%", delta_color="inverse")
    c3.metric("Bônus Redutor", f"R$ {v_redutor:,.2f}")
    c4.metric("Modelo", "Simplificado" if is_simp else "Deduções")

    st.divider()
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Líquido', 'INSS', 'IRRF'],
            values=[v_liquido, v_inss, v_irrf],
            hole=.5, marker=dict(colors=['#2ecc71', '#e74c3c', '#f1c40f'])
        )])
        fig_donut.update_layout(title="Distribuição Percentual")
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_r:
        st.subheader("📝 Resumo")
        res_df = pd.DataFrame({"Descrição": ["Bruto", "INSS", "IRRF", "Líquido"], 
                                "Valor": [s_bruto, v_inss, v_irrf, v_liquido]})
        st.table(res_df.set_index("Descrição"))

# --- CONTEÚDO DA ABA 2 ---
with tab_grafico:
    st.subheader("Evolução da Carga Tributária")
    st.write("Veja como o INSS e o IRRF se comportam conforme seu salário aumenta.")

    # Gerar dados para o gráfico (0 a 100k)
    faixas = np.linspace(0, 100000, 200)
    dados_curva = [calcular_completo(f, deps) for f in faixas]
    
    df_curva = pd.DataFrame(dados_curva, columns=['INSS', 'IRRF', 'Líquido', 'Redutor', 'IsSimp'])
    df_curva['Bruto'] = faixas

    # Gráfico de Áreas Empilhadas
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=df_curva['Bruto'], y=df_curva['Líquido'], name='Salário Líquido', 
                         mode='lines', stackgroup='one', line=dict(color='#2ecc71')))
    fig_curva.add_trace(go.Scatter(x=df_curva['Bruto'], y=df_curva['INSS'], name='INSS', 
                         mode='lines', stackgroup='one', line=dict(color='#e74c3c')))
    fig_curva.add_trace(go.Scatter(x=df_curva['Bruto'], y=df_curva['IRRF'], name='IRRF', 
                         mode='lines', stackgroup='one', line=dict(color='#f1c40f')))

    fig_curva.update_layout(
        xaxis_title="Salário Bruto (R$)",
        yaxis_title="Composição (R$)",
        hovermode="x unicode",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_curva, use_container_width=True)
    
    st.warning("⚠️ Observe que o IRRF cresce exponencialmente em salários mais altos, enquanto o INSS estabiliza após o teto.")
