import os
import requests

BRAPI_TOKEN = os.getenv("BRAPI_TOKEN")
MEUS_TICKERS = os.getenv("MEUS_TICKERS", "")

tickers = [
    ticker.strip().upper()
    for ticker in MEUS_TICKERS.split(",")
    if ticker.strip()
]

url = "https://brapi.dev/api/quote/" + ",".join(tickers)

params = {
    "modules": "defaultKeyStatistics"
}

headers = {}

if BRAPI_TOKEN:
    headers["Authorization"] = f"Bearer {BRAPI_TOKEN}"

print(f"Solicitando dados para: {','.join(tickers)}")
print(f"URL: {url}")

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=30
)

print(f"Código de retorno do servidor Brapi: {response.status_code}")

if response.status_code != 200:
    print("Resposta da Brapi:")
    print(response.text)
    response.raise_for_status()

dados = response.json()

print("Dados recebidos com sucesso.")
