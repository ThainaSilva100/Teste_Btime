# Bibliotecas utilizadas
import requests
import csv
import time

# Definindo a chave da API
API_KEY = 'SUA_CHAVE_API' # Substitua por sua chave de API da Alpha Vantage

# URL base da API
BASE_URL = 'https://www.alphavantage.co/query'

# Função para fazer a requisição da API
def obter_cotacao_acao(acao):
    parametros = {
        'function': 'TIME_SERIES_INTRADAY', # Para obter dados em tempo real
        'symbol': acao, # O símbolo da ação
        'interval': '1min', # Intervalo de tempo (1 minuto)
        'apikey': API_KEY # Chave da API
    }

    # Enviando os parâmetros para acessar a API
    resposta = requests.get(BASE_URL, params=parametros)
    if resposta.status_code == 200: # Se retornar 200 funcionou
        return resposta.json()
    else:
        print(f"Erro ao acessar API para {acao}: {resposta.status_code}") # Mensagem de erro se não conseguir acessar
        return None

# Função para extrair a cotação mais recente
def extrair_dados(dados):
    try:
        ultima_chave = list(dados['Time Series (1min)'].keys())[0]
        dados_acao = dados['Time Series (1min)'][ultima_chave]
        preco_abertura = dados_acao['1. open']
        preco_fechamento = dados_acao['4. close']
        return preco_abertura, preco_fechamento
    except KeyError:
        return None, None

# Lista de ações que vamos buscar
acoes = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

# Preparar lista para armazenar os dados
dados_acoes = []

# Coletar as cotações de cada ação
for acao in acoes:
    print(f"Coletando dados para a ação {acao}...")
    dados = obter_cotacao_acao(acao)
    if dados:
        preco_abertura, preco_fechamento = extrair_dados(dados)
        if preco_abertura and preco_fechamento:
            dados_acoes.append([acao, preco_abertura, preco_fechamento])
        else:
            dados_acoes.append([acao, "Erro", "Erro"])
    time.sleep(12) # A API tem um limite de requisições por minuto, então aguardamos 12 segundos

# Salvar os dados em um arquivo CSV
with open('cotacoes_acoes_api.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Ação', 'Preço de Abertura', 'Preço de Fechamento'])
    writer.writerows(dados_acoes)

print("Dados coletados e salvos com sucesso!") # Mensagem de sucesso
