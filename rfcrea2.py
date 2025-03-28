import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
import base64
from io import BytesIO
from PIL import Image
import os

# Configuração inicial da página
st.set_page_config(page_title="Relatorio Obra/Serviço", layout="wide")

# Classe para gerar PDF com cabeçalho personalizado
class PDF(FPDF):
    def __init__(self, logo_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logo_path = logo_path
    
    def header(self):
        # Configurações do cabeçalho
        self.set_font('Arial', 'B', 16)
        
        # Adicionar logo centralizado
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # Centraliza a imagem (considerando largura A4 = 210mm)
                img_width = 40  # Largura da imagem em mm
                x_position = (210 - img_width) / 2  # Calcula posição X para centralizar
                self.image(self.logo_path, x=x_position, y=10, w=img_width)
                self.ln(20)  # Espaçamento após o logo
            except Exception as e:
                st.error(f"Erro ao carregar logo: {e}")
        
        # Título centralizado abaixo do logo
        self.cell(0, 10, 'Relatório de Fiscalização', 0, 1, 'C')
        self.ln(10)  # Espaçamento após o cabeçalho
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

# Função para buscar CEP via API
def buscar_cep(cep):
    try:
        cep = cep.replace("-", "").replace(".", "").strip()
        if len(cep) == 8:
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'erro' not in data:
                    return data
        return None
    except:
        return None

# Função para criar PDF
def criar_pdf(dados, logo_path):
    pdf = PDF(logo_path=logo_path, orientation='P', unit='mm', format='A4')
    pdf.set_title("Relatório de Fiscalização")
    pdf.set_author("Sistema de Fiscalização")
    
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Seção de Endereço
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'ENDEREÇO DO EMPREENDIMENTO', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    pdf.cell(40, 10, 'Logradouro:', 0, 0)
    pdf.cell(0, 10, f"{dados['tipo_logradouro']} {dados['logradouro']}, {dados['numero']}", 0, 1)
    
    pdf.cell(40, 10, 'Bairro:', 0, 0)
    pdf.cell(0, 10, dados['bairro'], 0, 1)
    
    pdf.cell(40, 10, 'Município:', 0, 0)
    pdf.cell(0, 10, dados['municipio'], 0, 1)
    
    pdf.cell(40, 10, 'CEP:', 0, 0)
    pdf.cell(0, 10, dados['cep'], 0, 1)
    
    pdf.cell(40, 10, 'Coordenadas:', 0, 0)
    pdf.cell(0, 10, f"Lat: {dados['latitude']}, Long: {dados['longitude']}", 0, 1)
    
    pdf.ln(10)
    
    # Seção do Contratante
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'IDENTIFICAÇÃO DO CONTRATANTE', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    pdf.cell(40, 10, 'Nome:', 0, 0)
    pdf.cell(0, 10, dados['nome_contratante'], 0, 1)
    
    pdf.cell(40, 10, 'CPF/CNPJ:', 0, 0)
    pdf.cell(0, 10, dados['cpf_cnpj'], 0, 1)
    
    pdf.ln(10)
    
    # Seção de Atividade
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'ATIVIDADE DESENVOLVIDA', 0, 1)
    pdf.set_font('Arial', '', 12)
    
    pdf.cell(60, 10, 'Característica:', 0, 0)
    pdf.cell(0, 10, dados['caracteristica'], 0, 1)
    
    pdf.cell(60, 10, 'Fase:', 0, 0)
    pdf.cell(0, 10, dados['fase'], 0, 1)
    
    pdf.cell(60, 10, 'Nº de pavimentos:', 0, 0)
    pdf.cell(0, 10, dados['num_pavimentos'], 0, 1)
    
    pdf.cell(60, 10, 'Quantificação:', 0, 0)
    pdf.cell(0, 10, dados['quantificacao'], 0, 1)
    
    pdf.cell(60, 10, 'Unidade de medida:', 0, 0)
    pdf.cell(0, 10, dados['unidade_medida'], 0, 1)
    
    pdf.cell(60, 10, 'Natureza:', 0, 0)
    pdf.cell(0, 10, dados['natureza'], 0, 1)
    
    pdf.cell(60, 10, 'Tipo de Construção:', 0, 0)
    pdf.cell(0, 10, dados['tipo_construcao'], 0, 1)
    
    return pdf

# Barra lateral com menu
with st.sidebar:
    st.title("Menu")
    opcao = st.radio("Selecione o ambiente:", ("OBRA", "EMPRESA", "EVENTOS"))

# Conteúdo principal baseado na seleção
if opcao == "OBRA":
    # Caminho do logo
    logo_path = "10.png"
    
    # Verifica se o logo existe
    if not os.path.exists(logo_path):
        st.warning(f"Arquivo de logo não encontrado em: {logo_path}")
        logo_path = None
    
    # Exibir logo e título na página web
    if logo_path and os.path.exists(logo_path):
        st.image(logo_path, width=400)
    st.title("Relatório de Fiscalização")
    
    # Seção de Endereço
    st.header("ENDEREÇO DO EMPREENDIMENTO")
    
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.text_input("LATITUDE")
    with col2:
        longitude = st.text_input("LONGITUDE")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        tipo_logradouro = st.selectbox("Tipo", ["Avenida", "Rua", "Rodovia", "Estrada", "Viela", "Alameda"])
    with col2:
        logradouro = st.text_input("LOGRADOURO")
    with col3:
        numero = st.text_input("Nº")
    
    # Novos campos: Bairro e Município
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        bairro = st.text_input("BAIRRO")
    with col2:
        municipios_rj = [
            "Angra dos Reis", "Aperibé", "Araruama", "Areal", "Armação de Búzios",
            "Arraial do Cabo", "Barra do Piraí", "Barra Mansa", "Belford Roxo", "Bom Jardim",
            "Bom Jesus do Itabapuana", "Cabo Frio", "Cachoeiras de Macacu", "Cambuci", "Carapebus", "Comendador Levy Gasparian",
            "Campos dos Goytacazes", "Cantagalo", "Cardoso Moreira", "Carmo", "Casimiro de Abreu", "Conceição de Macabu",
            "Cordeiro", "Duas Barras", "Duque de Caxias", "Engenheiro Paulo de Frontim", "Guapimirim", "Iguaba Grande", "Itaborai", "Itaguai"
            "Italva", "Itaocara", "Itaperuna", "Itatiaia", "Japeri", "Laje do Muriaé", "Macaé", "Macuco", "Magé", "Mangaratiba",
            "Maricá", "Mendes", "Mesquita", "Miguel Pereira", "Miracema", "Natividade", "Nilópolis", "Niterói", "Nova Friburgo",
            "Nova Iguaçu", "Paracambi", "Paraiba do Sul", "Paraty", "Paraty", "Paty do Alferes", "Petrópolis", "Pinheiral", 
            "Pirai", "Porciúncula", "Porto Real", "Quatis", "Queimados", "Quissamã", "Resende", "Rio Bonito", "Rio Claro", "Rio das Flores",
            "Rio das Ostras", "Rio de Janeiro", "Santa Maria Madalena", "Santo Antônio de Pádua", "São Francisco de Itabapoana","São Fidélis",
            "São Gonçalo", "São João da Barra", "São João de Meriti", "São José de Ubá", "São José do Vale do Rio Preto", "São Pedro da Aldeia",
            "São Sebastião do Alto", "Sapucaia", "Saquarema", "Seropédica", "Silva Jardim", "Sumidouro", "Tanguá", "Teresópolis", "Trajano de Moraes",
            "Três Rios", "Valença", "Varre-Sai", "Vassouras","Volta Redonda", 
        ]
        municipio = st.selectbox("MUNICÍPIO", municipios_rj)
    with col3:
        cep = st.text_input("CEP", max_chars=9)
    
    # Botão de buscar CEP
    if st.button("Buscar CEP"):
        dados_cep = buscar_cep(cep)
        if dados_cep:
            st.success("CEP encontrado!")
            if 'logradouro' in dados_cep:
                st.session_state.logradouro = dados_cep['logradouro']
            if 'bairro' in dados_cep:
                st.session_state.bairro = dados_cep['bairro']
            st.rerun()
        else:
            st.error("CEP não encontrado ou inválido")
    
    # Seção do Contratante
    st.header("IDENTIFICAÇÃO DO CONTRATANTE")
    nome_contratante = st.text_input("NOME")
    cpf_cnpj = st.text_input("CPF/CNPJ")
    
    # Seção de Atividade
    st.header("ATIVIDADE DESENVOLVIDA")
    caracteristica = st.text_input("Característica")
    fase = st.selectbox("Fase", ["Acabamento", "Licitação", "Execução", "Conclusão"])
    num_pavimentos = st.number_input("Nº de pavimentos", min_value=0, step=1)
    quantificacao = st.text_input("Quantificação")
    unidade_medida = st.selectbox("Unidade de medida", ["m²", "m³", "un", "kg", "ton"])
    natureza = st.selectbox("Natureza", ["Pública", "Privada", "Mista"])
    tipo_construcao = st.selectbox("Tipo de Construção", ["Residencial", "Comercial", "Industrial", "Infraestrutura"])
    
    # Botão de submit principal
    if st.button("Gerar Relatório PDF"):
        if not logradouro or not nome_contratante or not cpf_cnpj:
            st.error("Preencha os campos obrigatórios!")
        else:
            dados = {
                'latitude': latitude,
                'longitude': longitude,
                'tipo_logradouro': tipo_logradouro,
                'logradouro': logradouro,
                'numero': numero,
                'bairro': bairro,
                'municipio': municipio,
                'cep': cep,
                'nome_contratante': nome_contratante,
                'cpf_cnpj': cpf_cnpj,
                'caracteristica': caracteristica,
                'fase': fase,
                'num_pavimentos': str(num_pavimentos),
                'quantificacao': quantificacao,
                'unidade_medida': unidade_medida,
                'natureza': natureza,
                'tipo_construcao': tipo_construcao
            }
            
            pdf = criar_pdf(dados, logo_path)
            
            pdf_bytes = BytesIO()
            pdf.output(pdf_bytes)
            pdf_bytes = pdf_bytes.getvalue()
            
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="relatorio_obra.pdf">Clique aqui para baixar o relatório em PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            st.success("Relatório gerado com sucesso! Clique no link acima para baixar.")

elif opcao == "EMPRESA":
    st.title("Cadastro de Empresa")
    st.write("Área em desenvolvimento para cadastro de empresas.")

elif opcao == "EVENTOS":
    st.title("Registro de Eventos")
    st.write("Área em desenvolvimento para registro de eventos.")