import streamlit as st

# Configuração da página
st.set_page_config(page_title="Calculadora IRRF 2026", page_icon="💰", layout="centered")

st.title("💰 Calculadora de Salário Líquido 2026")
st.markdown("Cálculo baseado na nova isenção de **R$ 5.000,00** (Regras SECOM/2026).")

# Sidebar para entradas
with st.sidebar:
    st.header("Entradas")
    salario_bruto = st.number_input("Salário Bruto (R$):", min_value=0.0, value=5001.0, step=100.0)
    dependentes = st.number_input("Número de Dependentes:", min_value=0, value=0, step=1)

# --- LÓGICA DE CÁLCULO ---

# 1. INSS (Arredondado)
if salario_bruto <= 1621.00:
    inss = round(salario_bruto * 0.075, 2)
elif salario_bruto <= 2902.84:
    inss = round((salario_bruto * 0.09) - 24.32, 2)
elif salario_bruto <= 4354.27:
    inss = round((salario_bruto * 0.12) - 111.40, 2)
else:
    valor_base_inss = min(salario_bruto, 8475.55)
    inss = round((valor_base_inss * 0.14) - 198.49, 2)

# 2. Escolha da Dedução (Simplificado vs Legal)
deducao_dep = round(dependentes * 189.59, 2)
deducoes_legais = round(inss + deducao_dep, 2)
desconto_simp = 607.20

escolha_simplificado = desconto_simp > deducoes_legais
melhor_deducao = max(deducoes_legais, desconto_simp)
base_irrf = round(max(0.0, salario_bruto - melhor_deducao), 2)

# 3. IRRF Tabela Progressiva
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

# 4. Redutor SECOM 2026
redutor_2026 = 0.0
if 5000.00 < salario_bruto <= 7350.00:
    redutor_2026 = round(978.62 - (0.133145 * salario_bruto), 2)
elif salario_bruto <= 5000.00:
    redutor_2026 = irrf_bruto 

irrf_final = round(max(0.0, irrf_bruto - redutor_2026), 2)
salario_liquido = round(salario_bruto - inss - irrf_final, 2)

# --- INTERFACE DE RESULTADOS (Com formatação de 2 casas decimais) ---

c1, c2, c3 = st.columns(3)
c1.metric("Salário Líquido", f"R$ {salario_liquido:,.2f}")
c2.metric("INSS", f"R$ {inss:,.2f}")
c3.metric("IRRF Final", f"R$ {irrf_final:,.2f}")

st.divider()

with st.expander("📊 Detalhamento Técnico"):
    st.write(f"**Base de Cálculo IRPF:** R$ {base_irrf:,.2f}")
    st.write(f"**Modelo de Desconto:** {'Simplificado' if escolha_simplificado else 'Deduções Legais'}")
    st.write(f"**Imposto Bruto:** R$ {irrf_bruto:,.2f}")
    st.write(f"**Redutor Especial 2026:** R$ {redutor_2026:,.2f}")

st.caption("Nota: Cálculos baseados na tabela vigente para o ano-calendário 2026.")
