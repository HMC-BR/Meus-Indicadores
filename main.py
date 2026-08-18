import os
import requests

def gerar_tabela_financeira():
    token = os.environ.get("BRAPI_TOKEN")
    tickers_raw = os.environ.get("MEUS_TICKERS") 
    
    if not token or not tickers_raw:
        print("❌ Erro: Configurações faltando nos Secrets.")
        return

    tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    tickers_str = ",".join(tickers)
    url = f"https://brapi.dev{tickers_str}?token={token}&modules=defaultKeyStatistics"
    
    try:
        response = requests.get(url, timeout=20)
        data = response.json()
    except Exception as e:
        print(f"❌ Erro ao conectar à API Brapi: {e}")
        return

    if "results" not in data:
        print("❌ Erro no retorno da API.")
        return

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
            preco = str(info.get("regularMarketPrice", 0)).replace('.', ',')
            stats = info.get("defaultKeyStatistics", {})
            pvp_raw = stats.get("priceToBook", "N/A") if stats else "N/A"
            pvp = str(pvp_raw).replace('.', ',') if pvp_raw != "N/A" else "N/A"
            dy_raw = stats.get("yield", 0) if stats else 0
            dy = f"{(dy_raw * 100):.2f}%".replace('.', ',') if (dy_raw and dy_raw != "N/A") else "0,00%"
            
            html_content += f"<tr><td>{ticker}</td><td>{nome}</td><td>{preco}</td><td>{pvp}</td><td>{dy}</td></tr>"
        else:
            html_content += f"<tr><td>{ticker}</td><td>Não encontrado</td><td></td><td></td><td></td></tr>"

    html_content += "</table></body></html>"

    os.makedirs("public_html", exist_ok=True)
    with open("public_html/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("🚀 Sucesso!")

if __name__ == "__main__":
    gerar_tabela_financeira()
  
