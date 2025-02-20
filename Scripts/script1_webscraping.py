# Bibliotecas utilizadas
import time
import random
import csv
import os
import zipfile
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
    
# URL para baixar o ChromeDriver
CHROMEDRIVER_URL = "https://storage.googleapis.com/chrome-for-testing-public/133.0.6943.126/win64/chromedriver-win64.zip"
CHROMEDRIVER_ZIP = "chromedriver.zip" # Nome da pasta zip onde está o Chromedriver
CHROMEDRIVER_FOLDER = "chromedriver-win64" # Nome da pasta do Chromedriver

# Baixa o arquivo ChromeDriver em ZIP se não existir
def download_chromedriver():
    if not os.path.exists(CHROMEDRIVER_ZIP):
        print("Baixando ChromeDriver...")
        response = requests.get(CHROMEDRIVER_URL, stream=True)
        with open(CHROMEDRIVER_ZIP, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Download concluído.")

# Extrai os arquivos da pasta ZIP
def extract_chromedriver():
    if not os.path.exists(CHROMEDRIVER_FOLDER):
        print("Extraindo ChromeDriver...")
        with zipfile.ZipFile(CHROMEDRIVER_ZIP, "r") as zip_ref:
            zip_ref.extractall(".")
        print("Extração concluída.")

# Configuração do Chrome com bloqueios comuns de scraping evitados
def start_chrome():
    chromedriver_path = os.path.join(CHROMEDRIVER_FOLDER, "chromedriver.exe")

    # Mensagem de erro para caso não exista o arquivo Chromedriver no diretório
    if not os.path.exists(chromedriver_path):
        print("Erro: ChromeDriver não encontrado!")
        return

    service = Service(chromedriver_path) # Instanciando o arquivo Chromedriver
    options = Options() # Instanciando a variável para evitar bloqueios na aplicação

    # Evitando bloqueios:
    options.add_argument("--disable-blink-features=AutomationControlled")  # Remove flag que denuncia Selenium
    options.add_argument("--start-maximized")  # Maximiza a janela
    options.add_argument("--disable-extensions")  # Desativa extensões
    options.add_argument("--disable-popup-blocking")  # Desativa bloqueios de pop-up
    options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória em servidores Linux
    options.add_argument("--no-sandbox")  # Necessário para algumas execuções

    # Função para gerar user-agent aleatório (alterando caracteres da URL para evitar que a automação seja detectada)
    def obter_user_agent():
        ua = UserAgent()
        return ua.random
    
    # Alterar o User-Agent
    user_agent = obter_user_agent()
    options.add_argument(f"user-agent={user_agent}")

    # Instanciando o Chrome
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Baixando o Chrome e extraindo arquivo Chromedriver
if not os.path.exists(CHROMEDRIVER_FOLDER):
    download_chromedriver()
    extract_chromedriver()

# Inicia o Chrome e acessa o site Yahoo Finance 
driver = start_chrome()

# URL do site que vamos navegar
url = "https://finance.yahoo.com"

# Ações que vamos buscar as cotações
acoes = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

# Preparar lista para armazenar os dados
dados_acoes = []

# Abrir a página do Yahoo Finance
driver.get(url)

# Tempo para a página carregar
time.sleep(random.uniform(2, 5)) # Pausa entre 2 e 5 segundos

# Coletar as cotações de cada ação
for acao in acoes:
    try:
        # Encontrar a barra de pesquisa e buscar a ação
        search_box = driver.find_element(By.ID, "ybar-sbq")
        search_box.clear() # Limpar a busca anterior
        search_box.send_keys(acao) 
        search_box.send_keys(Keys.RETURN) # Pressionar Enter
        
        # Tempo para a página carregar
        time.sleep(random.uniform(3, 6)) # Pausa entre 3 e 6 segundos

        # Coletar a cotação da ação
        cotacao = driver.find_element(By.XPATH, '/html/body/div[2]/main/section/section/section/article/section[1]/div[2]/div[1]/section/div/div/section/div[1]').text
        dados_acoes.append([acao, cotacao])
        print(f"Dados para {acao} coletados com sucesso!") # Mensagem de sucesso
    
    except Exception as e:
        print(f"Erro ao coletar dados para {acao}: {e}") # Mensagem de erro
        dados_acoes.append([acao, "Erro"])

# Fechar o navegador após a coleta de dados
driver.quit()

# Salvar os dados coletados em um arquivo CSV no diretório
with open('cotacoes_acoes.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Ação', 'Cotação'])
    writer.writerows(dados_acoes)

# Limpeza: Exclui o arquivo ZIP e a pasta descompactada do Chromedriver
    if os.path.exists(CHROMEDRIVER_ZIP):
        os.remove(CHROMEDRIVER_ZIP)
        print(f"{CHROMEDRIVER_ZIP} excluído com sucesso.")

    if os.path.exists(CHROMEDRIVER_FOLDER):
        shutil.rmtree(CHROMEDRIVER_FOLDER)
        print(f"Pasta {CHROMEDRIVER_FOLDER} excluída com sucesso.")

print("Dados coletados e salvos com sucesso!") # Mensagem de sucesso