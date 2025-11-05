import base64
from openai import AzureOpenAI
from configparser import ConfigParser, ExtendedInterpolation
import httpx
import numpy as np
import os
import shutil
from pdf2image import convert_from_path
import pandas as pd

# ============================================================
# CONFIGURAÇÕES DE CLIENTE AZURE OPENAI
# ============================================================

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('config.ini', 'UTF-8')

# Cliente HTTP com certificado Petrobras
http_client = httpx.Client(verify='petrobras-ca-root.pem')

client = AzureOpenAI(
    api_key=config['OPENAI']['OPENAI_API_KEY'],  
    api_version=config['OPENAI']['OPENAI_API_VERSION'],
    base_url=config['OPENAI']['AZURE_OPENAI_BASE_URL'],
    http_client=http_client
)

MODEL_DEPLOYMENT_ID = 'gpt-4o-petrobras'

print(http_client)
print(client)

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

diretorio_pdf = r"C:\Users\U33V\OneDrive - PETROBRAS\Desktop\python_old\docs_p_converter"
diretorio_to_pdf = r"C:\Users\U33V\OneDrive - PETROBRAS\Desktop\python_old\docs_p_converter\TEMP"

# Garante que o diretório de destino existe
os.makedirs(diretorio_to_pdf, exist_ok=True)

# Percorre os arquivos no diretório
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

df.to_csv("analise.csv", index=False)
print("Arquivo analise.csv salvo com sucesso!")

# Exibe as respostas
print(df["resposta"])
