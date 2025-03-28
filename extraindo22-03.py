import os
import re
import PyPDF2
import pandas as pd
import streamlit as st
from fpdf import FPDF
from io import BytesIO
from tempfile import NamedTemporaryFile

# Configuração inicial da página (elementos permanentes)
st.set_page_config(page_title="Extrator de Vínculos e S.I", layout="wide")
st.image('10.png', width=500)
st.title('CONSELHO REGIONAL DE ENGENHARIA E AGRONOMIA DO RIO DE JANEIRO')
st.header('RELATÓRIO de VÍNCULOS E S. I')

def extrair_texto_pdf(caminho_pdf):
    with open(caminho_pdf, 'rb') as arquivo:
        leitor = PyPDF2.PdfReader(arquivo)
        texto = ''
        for pagina in leitor.pages:
            texto += pagina.extract_text()
        return texto

def extrair_dados(texto):
    dados = {
        'Arquivo': '',
        'Contratados': '',
        'Vínculos': 0,
        'Ofícios': '',
        'S.I': 0
    }
    
    # Extrair todos os RESPONSAVEL TECNICO
    responsaveis = re.findall(r'RESPONSAVEL TECNICO\s*:\s*(.*?)(?:\n|$)', texto, re.IGNORECASE)
    if responsaveis:
        dados['Contratados'] += '; '.join([r.strip() for r in responsaveis if r.strip()]) + '; '
        dados['Vínculos'] += len(responsaveis)
    
    # Extrair todos os CONTRATADO
    contratados = re.findall(r'CONTRATADO\s*:\s*(.*?)(?:\n|$)', texto, re.IGNORECASE)
    if contratados:
        dados['Contratados'] += '; '.join([c.strip() for c in contratados if c.strip()]) + '; '
        dados['Vínculos'] += len(contratados)
    
    # Remover o último '; ' se existir
    dados['Contratados'] = dados['Contratados'].rstrip('; ')
    
    # Extrair Ofícios (capturar texto após "OFÍCIO - ")
    oficios = re.findall(r'OFÍCIO\s*-\s*(.*?)(?:\n|$)', texto, re.IGNORECASE)
    if oficios:
        dados['Ofícios'] = '; '.join([oficio.strip() for oficio in oficios if oficio.strip()])
        dados['S.I'] = len(oficios)
    
    return dados

def processar_pdfs(pdfs):
    dados_totais = []
    for pdf in pdfs:
        with NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf.getbuffer())
            tmp_path = tmp.name
        
        texto = extrair_texto_pdf(tmp_path)
        dados = extrair_dados(texto)
        dados['Arquivo'] = pdf.name
        dados_totais.append(dados)
        
        os.unlink(tmp_path)
    
    df = pd.DataFrame(dados_totais)
    
    # Adicionar linha de totais
    total_vinculos = df['Vínculos'].sum()
    total_si = df['S.I'].sum()
    
    linha_total = pd.DataFrame({
        'Arquivo': ['TOTAL'],
        'Contratados': [''],
        'Vínculos': [total_vinculos],
        'Ofícios': [''],
        'S.I': [total_si]
    })
    
    df = pd.concat([df, linha_total], ignore_index=True)
    return df

def gerar_relatorio_pdf(df):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # Configurações do PDF
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'RESULTADOS VÍNCULOS S.I', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font('Arial', '', 10)
    
    # Cabeçalho da tabela
    col_widths = [40, 50, 20, 50, 20]
    headers = ['Arquivo', 'Contratados', 'Vínculos', 'Ofícios', 'S.I']
    
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
    pdf.ln()
    
    # Conteúdo da tabela
    for _, row in df.iterrows():
        for i, col in enumerate(df.columns):
            pdf.cell(col_widths[i], 10, str(row[col]), 1, 0, 'C')
        pdf.ln()
    
    # Rodapé com totais
    pdf.ln(10)
    pdf.cell(0, 10, f'Total de Vínculos: {df["Vínculos"].iloc[-1]}', 0, 1)
    pdf.cell(0, 10, f'Total de S.I: {df["S.I"].iloc[-1]}', 0, 1)
    
    return pdf

def main():
    # Elementos da aplicação (abaixo dos elementos permanentes)
    st.subheader("Extrator de Vínculos e S.I de PDFs")
    
    uploaded_files = st.file_uploader("Carregue os arquivos PDF", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        df = processar_pdfs(uploaded_files)
        
        st.success("Processamento concluído!")
        st.dataframe(df)
        
        # Botão para baixar Excel
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button(
            label="Baixar Planilha Excel",
            data=excel_buffer,
            file_name="resultados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Botão para gerar relatório PDF
        if st.button("Emitir Relatório PDF"):
            pdf = gerar_relatorio_pdf(df)
            
            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_bytes = pdf_buffer.getvalue()
            
            st.download_button(
                label="Baixar Relatório PDF",
                data=pdf_bytes,
                file_name="RESULTADOS_VINCULOS_SI.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()