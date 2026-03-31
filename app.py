import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. Configuração e Estilo Customizado
st.set_page_config(page_title="IRRF 2026 Pro", page_icon="📈", layout="wide")

# CSS para injetar um visual de "Card" sombreado
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { color: #2E7D32; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Dashboard de Planejamento Tributário 2026")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Dados de Entrada")
    salario_bruto = st.number_input("Salário Bruto (R$):", min_value=0.0, value=5001.0, step=100.0)
    dependentes = st.number_input("Dependentes:", min_value=0, value=0)
    st.divider()
    st.markdown("### 💡 Insights")
    st.write("O cálculo prioriza automaticamente o modelo mais vantajoso (Simplificado vs Legal).")

# --- MOTOR DE CÁLCULO (Omitido aqui por brevidade, mantém o mesmo que validamos) ---
# [Insira aqui a lógica de INSS, Base IR, Redutor e IR Final que usamos acima]
# (Apenas certifique-se de manter as variáveis: inss, irrf_final, salario_liquido, etc.)

# --- INTERFACE DASHBOARD ---

# KPIs Principais em Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Líquido Mensal", f"R$ {salario_liquido:,.2f}")
with c2:
    st.metric("Custo Tributário", f"R$ {inss + irrf_final:,.2f}", f"{aliquota_efetiva}%", delta_color="inverse")
with c3:
    st.metric("Bônus Redutor 2026", f"R$ {redutor_2026:,.2f}")
with c4:
    st.metric("Modelo Aplicado", "Simplificado" if escolha_simplificado else "Deduções")

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    # Gráfico de Rosca Estilizado
    fig = go.Figure(data=[go.Pie(
        labels=['Líquido', 'INSS', 'IRRF'],
        values=[salario_liquido, inss, irrf_final],
        hole=.5,
        marker=dict(colors=['#00C853', '#FF5252', '#FFD600']),
        textinfo='percent+label'
    )])
    fig.update_layout(title_text="Distribuição do Salário Bruto", margin=dict(t=50, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📝 Resumo para Exportação")
    # Tabela de conferência rápida
    df_resumo = pd.DataFrame({
        "Descrição": ["Bruto", "INSS", "IRRF", "Líquido"],
        "Valor (R$)": [salario_bruto, inss, irrf_final, salario_liquido]
    })
    st.table(df_resumo.set_index("Descrição"))
    
    # Botão de Exportação (Útil para suas planilhas de Engenharia)
    csv = df_resumo.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar CSV", data=csv, file_name="simulacao_irrf_2026.csv", mime="text/csv")

st.success(f"Tudo pronto! Com um salário de R$ {salario_bruto:,.2f}, sua carga tributária real é de apenas {aliquota_efetiva}%.")
