import os
import requests
import sys

def gerar_tabela_financeira():
    # Coleta os segredos removendo espaços ocultos
    token = os.environ.get("BRAPI_TOKEN", "").strip()
    tickers_raw = os.environ.get("MEUS_TICKERS", "").strip() 
    
    if not token or not tickers_raw:
        print("❌ Erro: BRAPI_TOKEN ou MEUS_TICKERS não configurados nos Secrets.")
        sys.exit(1)

    # Limpeza de espaços nos tickers
    tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    tickers_str = ",".join(tickers)
    
    print(f"🔍 Solicitando dados para: {tickers_str}")
    url = f"https://brapi.dev{tickers_str}?token={token}&modules=defaultKeyStatistics"
    
    try:
        response = requests.get(url, timeout=25)
        print(f"📊 Código de retorno do servidor Brapi: {response.status_code}")
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Falha na conexão ou na requisição: {e}")
        sys.exit(1)

    if "results" not in data:
        print("❌ Resposta da API não possui o campo 'results'.")
        sys.exit(1)

    html_content = """
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <table border="1" id="dados-b3">
            <tr>
                <th>Ticker</th>
                <th>Nome</th>
                <th>Preco</th>
                <th>P_VP</th>
                <th>DY</th>
            </tr>
    """

    for ticker in tickers:
        info = next((res for res in data["results"] if res.get("symbol") == ticker), None)
        if info:
            nome = info.get("longName", "N/A")
            
            # Tratamento correto e limpo do preço comercializado
            preco_raw = info.get("regularMarketPrice", 0)
            preco = str(preco_raw).replace('.', ',')
            
            stats = info.get("defaultKeyStatistics", {}) or {}
            pvp_raw = stats.get("priceToBook", "N/A")
            pvp = str(pvp_raw).replace('.', ',') if pvp_raw != "N/A" else "N/A"
            
            dy_raw = stats.get("yield", 0)
            dy = f"{(dy_raw * 100):.2f}%".replace('.', ',') if (dy_raw and dy_raw != "N/A") else "0,00%"
            
            html_content += f"<tr><td>{ticker}</td><td>{nome}</td><td>{preco}</td><td>{pvp}</td><td>{dy}</td></tr>"
        else:
            html_content += f"<tr><td>{ticker}</td><td>Não encontrado</td><td></td><td></td><td></td></tr>"

    html_content += "</table></body></html>"

    # CRIAÇÃO DA PASTA (Corrige o erro da linha 43 do seu log)
    os.makedirs("public_html", exist_ok=True)
    with open("public_html/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("🚀 Sucesso! Tabela HTML construída com sucesso na pasta public_html.")

if __name__ == "__main__":
    gerar_tabela_financeira()
