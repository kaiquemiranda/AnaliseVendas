import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Vendas de Peças", layout="wide")
st.image('box7.png')
st.title("Análise de Vendas")

uploaded_file = st.file_uploader("Carregar arquivo Excel", type=["xls", "xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=5)


    vendas_por_sku = df.groupby('SKU')[['Unidades', 'Título do anúncio']].sum().reset_index()

    vendas_por_sku = vendas_por_sku.sort_values(by='Unidades', ascending=False)
    st.markdown(f"Total: {df['Unidades'].sum()}")

    st.dataframe(vendas_por_sku)

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        vendas_por_sku.to_excel(writer, index=False, sheet_name='Vendas por SKU')

    buffer.seek(0)

    st.download_button(
        label="Baixar Excel",
        data=buffer,
        file_name="vendas_por_sku.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
