import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. Configuração e Estilo Customizado
st.set_page_config(page_title="IRRF 2026 Pro", page_icon="📈", layout="wide")

# CSS para injetar um visual de "Card" sombreado e cores consistentes
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stMetricValue"] { color: #2E7D32; font-weight: bold; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Dashboard de Planejamento Tributário 2026")
st.caption("Simulação baseada na nova regra de isenção de R$ 5.000,00 (SECOM)")

# --- SIDEBAR (INPUTS) ---
with st.sidebar:
    st.header("📋 Dados de Entrada")
    salario_bruto = st.number_input("Salário Bruto (R$):", min_value=0.0, value=5001.0, step=100.0)
    dependentes = st.number_input("Dependentes:", min_value=0, value=0)
    st.divider()
    st.markdown("### 💡 Insights")
    st.info("O cálculo prioriza automaticamente o modelo mais vantajoso: **Desconto Simplificado** (R$ 607,20) vs **Deduções Legais**.")

# --- MOTOR DE CÁLCULO (O que estava faltando) ---

# 1. INSS 2026
if salario_bruto <= 1621.00:
    inss = round(salario_bruto * 0.075, 2)
elif salario_bruto <= 2902.84:
    inss = round((salario_bruto * 0.09) - 24.32, 2)
elif salario_bruto <= 4354.27:
    inss = round((salario_bruto * 0.12) - 111.40, 2)
else:
    valor_base_inss = min(salario_bruto, 8475.55)
    inss = round((valor_base_inss * 0.14) - 198.49, 2)

# 2. Melhor Dedução (Simplificado vs Legal)
deducao_dep = round(dependentes * 189.59, 2)
deducoes_legais = round(inss + deducao_dep, 2)
desconto_simp = 607.20

escolha_simplificado = desconto_simp > deducoes_legais
melhor_deducao = max(deducoes_legais, desconto_simp)
base_irrf = round(max(0.0, salario_bruto - melhor_deducao), 2)

# 3. IRRF Tabela Progressiva 2026
if base_irrf <= 2428.80:
    irrf_bruto = 0.0
elif base_irrf <= 2826.65:
    irrf_bruto = (base_irrf * 0.075) - 182.16
elif base_irrf <= 3751.05:
    irrf_bruto = (base_irrf * 0.15) - 394.16
elif base_irrf <= 4664.68:
    irrf_bruto = (base_irrf * 0.225) - 675.49
else:
    irrf_bruto = (base_irrf * 0.275) - 908.73
irrf_bruto = round(max(0.0, irrf_bruto), 2)

# 4. Redutor Especial 2026 (Regra dos R$ 5.000)
redutor_2026 = 0.0
if 5000.00 < salario_bruto <= 7350.00:
    redutor_2026 = round(978.62 - (0.133145 * salario_bruto), 2)
elif salario_bruto <= 5000.00:
    redutor_2026 = irrf_bruto 

irrf_final = round(max(0.0, irrf_bruto - redutor_2026), 2)
salario_liquido = round(salario_bruto - inss - irrf_final, 2)
impostos_totais = round(inss + irrf_final, 2)
aliquota_efetiva = round((impostos_totais / salario_bruto) * 100, 2) if salario_bruto > 0 else 0

# --- INTERFACE DASHBOARD (EXIBIÇÃO) ---

# Linha 1: KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Líquido Mensal", f"R$ {salario_liquido:,.2f}")
with c2:
    st.metric("Custo Tributário", f"R$ {impostos_totais:,.2f}", f"{aliquota_efetiva}%", delta_color="inverse")
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
    st.subheader("📝 Resumo de Dados")
    df_resumo = pd.DataFrame({
        "Descrição": ["Bruto", "INSS", "IRRF", "Líquido"],
        "Valor (R$)": [salario_bruto, inss, irrf_final, salario_liquido]
    })
    st.table(df_resumo.set_index("Descrição"))
    
    # Exportação para CSV (estilo Excel)
    csv = df_resumo.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Planilha (CSV)", data=csv, file_name="simulacao_irrf_2026.csv", mime="text/csv")

st.success(f"Cálculo finalizado: Com um salário de R$ {salario_bruto:,.2f}, sua carga tributária real é de {aliquota_efetiva}%.")
