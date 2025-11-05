import openai
openai.__version__
import base64
from openai import AzureOpenAI
from configparser import ConfigParser, ExtendedInterpolation
import httpx
import numpy as np

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read('../../config-v1.x.ini', 'UTF-8')

http_client = httpx.Client(verify='../../petrobras-ca-root.pem')

client = AzureOpenAI(
    api_key=config['OPENAI']['OPENAI_API_KEY'],  
    api_version=config['OPENAI']['OPENAI_API_VERSION'],
    base_url=config['OPENAI']['AZURE_OPENAI_BASE_URL'],
    http_client=http_client
)

MODEL_DEPLOYMENT_ID = 'gpt-4o-petrobras'

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

import os
import shutil
from pdf2image import convert_from_path
import pandas as pd

# Caminho para o diretório dos arquivos PDF
diretorio_pdf = "C:\\Users\\U33V\\OneDrive - PETROBRAS\\Desktop\\python\\docs_p_converter\\"
diretorio_to_pdf = "C:\\Users\\U33V\\OneDrive - PETROBRAS\\Desktop\\python\\docs_p_converter\\TEMP\\"

# Percorre os arquivos no diretório
for arquivo in os.listdir(diretorio_pdf):
    
    # Verifica se o arquivo é uma imagem
    print(arquivo)
    if arquivo.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        # Copia o arquivo para o novo diretório
        caminho_imagem = os.path.join(diretorio_pdf, arquivo)
        print(caminho_imagem)
        shutil.copy(caminho_imagem, diretorio_to_pdf)
        print(f'Arquivo {arquivo} copiado com sucesso.')

    
    elif arquivo.endswith('.pdf'):
        caminho_arquivo = os.path.join(diretorio_pdf, arquivo)
        
        # Converte o arquivo PDF para imagens
        imagens = convert_from_path(caminho_arquivo,  500,poppler_path=r"C:\\Users\\U33V\\OneDrive - PETROBRAS\\Desktop\\python\\poppler-0.68.0\\bin")
        
        # Salva as imagens
        for i, imagem in enumerate(imagens):
            nome_imagem = f'{arquivo}_{i}.jpg' # ou outro formato de imagem desejado
            caminho_imagem = os.path.join(diretorio_to_pdf, nome_imagem)
            imagem.save(caminho_imagem, 'JPEG')
            
        print(f'Arquivo {arquivo} convertido com sucesso.')
    
  
# Percorre os arquivos no diretório convertido e pega somente as imagens e guarda em dataframe
arquivos=[]
for arquivo in os.listdir(diretorio_to_pdf):
    if arquivo.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        caminho_imagem = os.path.join(diretorio_to_pdf, arquivo)
        arquivos.append(caminho_imagem)

print(arquivos)
texts_in_data = [x for x  in arquivos]
df = pd.DataFrame(texts_in_data)

df.rename( columns={0 :'arquivo'}, inplace=True )


base64_imagens=[]
for index, row in df.iterrows():
    with open(row["arquivo"], 'rb') as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')
        base64_imagens.append(base64_image)

df["base64"]=base64_imagens

df


respostas=[]
for index, row in df.iterrows():
    messages=[
        {"role": "system", "content": 'Você deve ajudar o usuário numa tarefa de classificação e extração de informações sobre 3 tipos de imagens.'},
        {"role": "user", "content": [
            {
                'type': 'text',
                'text': 'Descreva o conteúdo da imagem com base na seguinte regra:  1-Se for uma nota fiscal, responda NOTAFISCAL | número da nota | valor total da nota. 2- Se for Certificado de Conteúdo Local, responda CERTIFICADO | número de certificado | percentual de conteúdo local. 3- Se for recibo, responda RECIBO | número do recibo | valor total.'
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{row['base64']}"
                }
            }
        ]}
    ]
    response = send_message(messages, engine=MODEL_DEPLOYMENT_ID)

    # Converte a string para UTF-8
    utf8_string = response.encode('utf-8')
    # Imprime a string UTF-8
    print(utf8_string.decode('utf-8'))
    respostas.append(utf8_string.decode('utf-8'))

df["resposta"]=respostas

df.to_csv("analise.csv")

df["resposta"]

