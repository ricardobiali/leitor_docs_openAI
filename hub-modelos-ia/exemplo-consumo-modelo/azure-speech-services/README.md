# Azure Speech Services

## Como usar

Verifique o [notebook com o exemplo de código](exemplo-transcricao-audio.ipynb) para acionar a API.

Os arquivos de áudio devem estar em uma URL pública ou em uma storage account da Azure com acesso via SAS (URL com assinatura de acesso compartilhado).

De posse da URL que aponta para os arquivos, deve-se acionar o método `Criar transcrição`.

Após criar a transcrição, o método que consulta a transcrição retorna um campo `status` que indica se o job já foi concluído.

Quando o status for `Suceeded`, deve-se acionar o método `Listar arquivos da transcrição` para obter as URLs dos arquivos contendo o resultado da operação.

## Observações

* Neste momento, somente está disponível a transcrição de áudio com os modelos pré-treinados da Azure.
* Recomendamos que as transcrições sejam excluídas (método `DELETE` da API) após serem copiadas para o sistema cliente.

## Métodos disponíveis

* Criar transcrição
* Consultar transcrição
* Listar arquivos da transcrição
* Consultar arquivo de transcriçao
* Listar locales disponíveis
* Atualizar transcrição
* Excluir transcrição

Consulte a referência completa no [portal do Hub de Modelos](https://apid-portal.petrobras.com.br/api-details#api=azure-speech-services) e no [site da Azure](https://learn.microsoft.com/en-us/rest/api/speechtotext/create-transcription/create-transcription?view=rest-speechtotext-v3.0&tabs=HTTP).

