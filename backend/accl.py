import base64
from openai import AzureOpenAI
from configparser import ConfigParser, ExtendedInterpolation
import httpx
import numpy as np
import os
import shutil
from pdf2image import convert_from_path
import pandas as pd
import json
from pathlib import Path

# ============================================================
# CONFIGURAÇÕES DE CLIENTE AZURE OPENAI
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BACKEND_DIR / "config.ini"

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read(CONFIG_PATH, encoding="utf-8")

# Cliente HTTP com certificado Petrobras
BACKEND_DIR = Path(__file__).resolve().parent
PEM_PATH = BACKEND_DIR / "petrobras-ca-root.pem"
http_client = httpx.Client(verify=str(PEM_PATH))

client = AzureOpenAI(
    api_key=config['OPENAI']['OPENAI_API_KEY'],  
    api_version=config['OPENAI']['OPENAI_API_VERSION'],
    base_url=config['OPENAI']['AZURE_OPENAI_BASE_URL'],
    http_client=http_client
)

MODEL_DEPLOYMENT_ID = 'gpt-4o-petrobras'

# ============================================================
# LER DIRETÓRIO DO ARQUIVO requests.json
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent  # raiz do projeto
FRONTEND_DIR = BASE_DIR / "frontend"
REQUESTS_FILE = FRONTEND_DIR / "requests.json"

# Lê o caminho da pasta informado pelo usuário
if REQUESTS_FILE.exists():
    with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        diretorio_pdf = Path(data.get("diretorio", "")).resolve()
else:
    raise FileNotFoundError(f"Arquivo {REQUESTS_FILE} não encontrado.")

if not diretorio_pdf.exists():
    raise ValueError(f"O diretório informado não existe: {diretorio_pdf}")

# Define diretório TEMP dentro do caminho do usuário
diretorio_to_pdf = diretorio_pdf / "TEMP"
os.makedirs(diretorio_to_pdf, exist_ok=True)

# Define caminho do Poppler dinamicamente (relativo ao projeto)
poppler_path = str(BASE_DIR / "poppler-0.68.0" / "bin")

# ============================================================
# FUNÇÃO PARA ENVIO DE MENSAGENS AO MODELO
# ============================================================

def send_message(messages, engine, max_response_tokens=500):
    response = client.chat.completions.create(
        model=engine,
        messages=messages,
        temperature=0.5,
        max_tokens=max_response_tokens,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

# ============================================================
# PROCESSAMENTO DE ARQUIVOS PDF E IMAGENS
# ============================================================

for arquivo in os.listdir(diretorio_pdf):
    print(arquivo)
    caminho_arquivo = os.path.join(diretorio_pdf, arquivo)

    # Copia imagens diretamente
    if arquivo.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        shutil.copy(caminho_arquivo, diretorio_to_pdf)
        print(f'Arquivo {arquivo} copiado com sucesso.')

    # Converte PDFs em imagens
    elif arquivo.lower().endswith('.pdf'):
        imagens = convert_from_path(
            caminho_arquivo,
            500,
            poppler_path=r"C:\Users\U33V\OneDrive - PETROBRAS\Desktop\python\reader_openAI\poppler-0.68.0\bin"
        )
        for i, imagem in enumerate(imagens):
            nome_imagem = f'{arquivo}_{i}.jpg'
            caminho_imagem = os.path.join(diretorio_to_pdf, nome_imagem)
            imagem.save(caminho_imagem, 'JPEG')
        print(f'Arquivo {arquivo} convertido com sucesso.')

# ============================================================
# CRIAÇÃO DO DATAFRAME DE IMAGENS
# ============================================================

arquivos = []
for arquivo in os.listdir(diretorio_to_pdf):
    if arquivo.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        caminho_imagem = os.path.join(diretorio_to_pdf, arquivo)
        arquivos.append(caminho_imagem)

print(arquivos)

df = pd.DataFrame(arquivos, columns=['arquivo'])

base64_imagens = []
for _, row in df.iterrows():
    with open(row["arquivo"], 'rb') as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')
        base64_imagens.append(base64_image)

df["base64"] = base64_imagens

# ============================================================
# ANÁLISE COM O MODELO
# ============================================================

respostas = []

for _, row in df.iterrows():
    messages = [
        {"role": "system", "content": 'Você deve ajudar o usuário numa tarefa de classificação e extração de informações sobre 3 tipos de imagens.'},
        {"role": "user", "content": [
            {
                'type': 'text',
                'text': (
                    'Descreva o conteúdo da imagem com base na seguinte regra: '
                    '1-Se for uma nota fiscal, responda NOTAFISCAL | número da nota | valor total da nota. '
                    '2- Se for Certificado de Conteúdo Local, responda CERTIFICADO | número de certificado | percentual de conteúdo local. '
                    '3- Se for recibo, responda RECIBO | número do recibo | valor total. '
                    '4- Se for Relatório de Medição (RM), responda REL_MEDICAO | número do relatório | valor bruto. '
                    '5- Se for outro tipo de documento, responda OUTRO | - | 0 .'
                )
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{row['base64']}"}
            }
        ]}
    ]
    response = send_message(messages, engine=MODEL_DEPLOYMENT_ID)

    # Converte a string para UTF-8 e imprime
    utf8_string = response.encode('utf-8')
    print(utf8_string.decode('utf-8'))
    respostas.append(utf8_string.decode('utf-8'))

df["resposta"] = respostas

# ============================================================
# SALVA RESULTADOS
# ============================================================

output_csv = BACKEND_DIR / "analise.csv"
df.to_csv(output_csv, index=False, encoding="utf-8-sig")
print(f"Arquivo analise.csv salvo com sucesso em: {output_csv}")

# Exibe as respostas
print(df["resposta"])
