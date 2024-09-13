import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO


st.set_page_config(page_title="Análise de Vendas Box 7", layout="wide")
st.image('box7.png')
st.title("Análise de Vendas")

uploaded_file = st.file_uploader("Carregar arquivo Excel", type=["xls", "xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=5)
    if df.empty or 'Título do anúncio' not in df.columns:
        # Se não funcionar, tentar ler pulando 6 linhas
        df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=6)

    palavras_chave = st.text_input("Digite as palavras-chave para buscar um produto.").strip()
    palavras_excluir = st.text_input("Digite as palavras-chave que deseja excluir da busca.").strip()

    if st.button("Buscar"):
        if palavras_chave:
            palavras_chave = palavras_chave.lower().split()
            palavras_excluir = palavras_excluir.lower().split() if palavras_excluir else []

            filtro_incluir = df['Título do anúncio'].str.contains(palavras_chave[0], case=False)
            for palavra in palavras_chave[1:]:
                filtro_incluir &= df['Título do anúncio'].str.contains(palavra, case=False)

            filtro_excluir = ~df['Título do anúncio'].str.contains(palavras_excluir[0], case=False) if palavras_excluir else True
            for palavra in palavras_excluir[1:]:
                filtro_excluir &= ~df['Título do anúncio'].str.contains(palavra, case=False)


            df_filtrado = df[filtro_incluir & filtro_excluir]

            if not df_filtrado.empty:
                st.dataframe(df_filtrado[['N.º de venda', 'SKU', 'Unidades', 'Data da venda', 'Título do anúncio',
                                          'Receita por produtos (BRL)', 'Tarifas de envio',
                                          'Tarifa de venda e impostos', 'Total (BRL)']])

                vendas_por_sku = df_filtrado.groupby('SKU')['Unidades'].sum().reset_index()

                vendas_por_sku = vendas_por_sku.sort_values(by='Unidades', ascending=False)
                st.markdown(f"Total: {df_filtrado['Unidades'].sum()}")
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



                fig = px.bar(vendas_por_sku,
                             x='SKU',
                             y='Unidades',
                             title=f'Produtos mais vendidos para as palavras-chave: {", ".join(palavras_chave).capitalize()}',
                             labels={'SKU': 'SKU', 'Unidades': 'Quantidade de Vendas'},
                             text_auto=True)

                st.plotly_chart(fig, use_container_width=True)



            else:
                st.warning("Nenhum resultado encontrado para as palavras-chave fornecidas.")
        else:
            st.info("Por favor, insira palavras-chave para realizar a busca.")
