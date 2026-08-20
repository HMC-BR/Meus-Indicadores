import os
import sys
import yfinance as yf

def gerar_tabela_financeira():
    # Coleta a lista de tickers salva no GitHub Secrets (Ex: PETR4,VALE3,HGLG11)
    tickers_raw = os.environ.get("MEUS_TICKERS", "").strip() 
    
    if not tickers_raw:
        print("❌ Erro: A variável MEUS_TICKERS não foi configurada nos Secrets.")
        sys.exit(1)

    # Limpa os tickers e adiciona o ".SA" necessário para o Yahoo Finance
    tickers_limpos = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    
    print(f"🔍 Buscando dados no Yahoo Finance para: {', '.join(tickers_limpos)}")

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

    for ticker in tickers_limpos:
        # Garante o sufixo .SA para ativos brasileiros no Yahoo
        ticker_yahoo = ticker if ticker.endswith(".SA") else f"{ticker}.SA"
        
        try:
            ativo = yf.Ticker(ticker_yahoo)
            info = ativo.info  # Puxa o dicionário completo de dados do ativo
            
            # Extração segura de dados mecânicos do Yahoo Finance
            nome = info.get("longName", "N/A")
            
            # Tenta pegar o preço atual por múltiplos campos comuns do Yahoo
            preco_raw = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("navPrice") or 0
            preco = str(round(preco_raw, 2)).replace('.', ',') if preco_raw else "0,00"
            
            # P/VP (priceToBook)
            pvp_raw = info.get("priceToBook", "N/A")
            pvp = str(round(pvp_raw, 2)).replace('.', ',') if isinstance(pvp_raw, (int, float)) else "N/A"
            
            # Dividend Yield (Muitos FIIs e ações guardam em dividendYield)
            dy_raw = info.get("dividendYield", 0) or info.get("trailingAnnualDividendYield", 0) or 0
            dy = f"{(dy_raw * 100):.2f}%".replace('.', ',')
            
            html_content += f"<tr><td>{ticker}</td><td>{nome}</td><td>{preco}</td><td>{pvp}</td><td>{dy}</td></tr>"
            print(f"✅ {ticker} processado com sucesso.")
            
        except Exception as e:
            print(f"⚠️ Erro ao processar o ticker {ticker}: {e}")
            html_content += f"<tr><td>{ticker}</td><td>Erro ao carregar</td><td></td><td></td><td></td></tr>"

    html_content += "</table></body></html>"

    # Salva o arquivo na pasta de publicação
    os.makedirs("public_html", exist_ok=True)
    with open("public_html/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("🚀 Sucesso! Tabela HTML construída com dados do Yahoo Finance.")

if __name__ == "__main__":
    gerar_tabela_financeira()
