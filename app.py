import streamlit as st
import plotly.graph_objects as go

# 1. Configuração do Layout Estilo Dashboard
st.set_page_config(page_title="Dashboard IRRF 2026", page_icon="📊", layout="wide")

# CSS para customizar a aparência dos cards
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E88E5; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Dashboard de Planejamento Tributário 2026")
st.caption("Simulação baseada na nova tabela de isenção de R$ 5.000,00")

# --- BARRA LATERAL (INPUTS) ---
with st.sidebar:
    st.header("⚙️ Parâmetros")
    salario_bruto = st.number_input("Salário Bruto Mensal (R$):", min_value=0.0, value=5001.0, step=100.0)
    dependentes = st.number_input("Número de Dependentes:", min_value=0, value=0, step=1)
    st.divider()
    st.info("Este dashboard utiliza a regra de transição da SECOM para rendas entre R$ 5.001 e R$ 7.350.")

# --- LÓGICA DE CÁLCULO (O "MOTOR" DO DASHBOARD) ---
# INSS
if salario_bruto <= 1621.00: inss = round(salario_bruto * 0.075, 2)
elif salario_bruto <= 2902.84: inss = round((salario_bruto * 0.09) - 24.32, 2)
elif salario_bruto <= 4354.27: inss = round((salario_bruto * 0.12) - 111.40, 2)
else:
    valor_base_inss = min(salario_bruto, 8475.55)
    inss = round((valor_base_inss * 0.14) - 198.49, 2)

# Melhor Dedução (Simplificado vs Legal)
deducao_dep = round(dependentes * 189.59, 2)
deducoes_legais = round(inss + deducao_dep, 2)
desconto_simp = 607.20
escolha_simplificado = desconto_simp > deducoes_legais
melhor_deducao = max(deducoes_legais, desconto_simp)
base_irrf = round(max(0.0, salario_bruto - melhor_deducao), 2)

# IRRF Tabela Progressiva
if base_irrf <= 2428.80: irrf_bruto = 0.0
elif base_irrf <= 2826.65: irrf_bruto = (base_irrf * 0.075) - 182.16
elif base_irrf <= 3751.05: irrf_bruto = (base_irrf * 0.15) - 394.16
elif base_irrf <= 4664.68: irrf_bruto = (base_irrf * 0.225) - 675.49
else: irrf_bruto = (base_irrf * 0.275) - 908.73
irrf_bruto = round(max(0.0, irrf_bruto), 2)

# Redutor Especial 2026
redutor_2026 = 0.0
if 5000.00 < salario_bruto <= 7350.00:
    redutor_2026 = round(978.62 - (0.133145 * salario_bruto), 2)
elif salario_bruto <= 5000.00:
    redutor_2026 = irrf_bruto 

irrf_final = round(max(0.0, irrf_bruto - redutor_2026), 2)
salario_liquido = round(salario_bruto - inss - irrf_final, 2)
impostos_totais = round(inss + irrf_final, 2)
aliquota_efetiva = round((impostos_totais / salario_bruto) * 100, 2) if salario_bruto > 0 else 0

# --- EXIBIÇÃO DO DASHBOARD ---

# Linha 1: Métricas Principais
c1, c2, c3, c4 = st.columns(4)
c1.metric("Líquido a Receber", f"R$ {salario_liquido:,.2f}")
c2.metric("Total Impostos", f"R$ {impostos_totais:,.2f}", delta=f"-{aliquota_efetiva}%", delta_color="inverse")
c3.metric("INSS", f"R$ {inss:,.2f}")
c4.metric("IRRF Final", f"R$ {irrf_final:,.2f}")

st.divider()

# Linha 2: Gráficos e Detalhes
col_grafico, col_detalhes = st.columns([2, 1])

with col_grafico:
    st.subheader("Composição do Rendimento Bruto")
    labels = ['Salário Líquido', 'INSS', 'IRRF']
    values = [salario_liquido, inss, irrf_final]
    colors = ['#2ecc71', '#e74c3c', '#f1c40f']
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=colors)])
    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=350)
    st.plotly_chart(fig, use_container_width=True)

with col_detalhes:
    st.subheader("Análise Técnica")
    st.write(f"**Base IR:** R$ {base_irrf:,.2f}")
    st.write(f"**Modelo:** {'Simplificado' if escolha_simplificado else 'Deduções Legais'}")
    st.write(f"**Benefício (Redutor):** R$ {redutor_2026:,.2f}")
    
    st.progress(aliquota_efetiva / 27.5 if aliquota_efetiva < 27.5 else 1.0)
    st.write(f"Alíquota Efetiva: **{aliquota_efetiva}%**")

st.info(f"💡 Dica: Ao usar o {('desconto simplificado' if escolha_simplificado else 'modelo de deduções')}, sua economia tributária foi maximizada automaticamente.")
