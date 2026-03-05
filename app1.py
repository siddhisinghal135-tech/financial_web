from flask import Flask, render_template, jsonify
import requests 
from flask_cors import CORS
import pandas as pd
import os
app=Flask(__name__)
CORS(app)
API_KEY="W8A7ZES3OO5558MJ"

@app.route("/")
def home():
    return render_template("codex.html")

@app.route("/analysis")
def analyse():
    url=f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=BOM:MARUTI&apikey={API_KEY}"
    response=requests.get(url)
    data_api=response.json()
    quote = data_api.get("Global Quote", {})
    cp = float(quote.get("05. price", 10000))
    op = float(quote.get("02. open", 9000))
    high = float(quote.get("03. high", 10200))
    low = float(quote.get("04. low", 8998))
    ch = quote.get("10. change percent", "2%")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "data.xlsx")
    d=pd.read_excel(file_path,sheet_name="DATA")
    bs_d=pd.read_excel(file_path,sheet_name="BALANCESHEET")
    pnl_d=pd.read_excel(file_path,sheet_name="PROFITLOSS")
    cf_d=pd.read_excel(file_path,sheet_name="CASHFLOW")
    
    rev=d["SALES"].pct_change().mean()*100
    pft=d["NET PROFIT"].pct_change().mean()*100
    
    pststatement=f"""Over the past five years,
the company has achieved an average annual revenue growth of {round(rev,2)}%,
along with an average profit growth of {round(pft,2)}%.
This reflects the company’s financial performance and growth consistency over time."""

    latest_profit = d["NET PROFIT"].iloc[-1]
    latest_equity = d["EQUITY"].iloc[-1]
    #pststatement="hello"
    ROE = round((latest_profit / latest_equity) * 100,2)
    roe=f"""
The company has maintained an average ROE of {ROE}%.
Return on Equity (ROE) measures how efficiently the company generates profit 
from shareholders' equity. A consistently high ROE indicates strong financial performance.
"""
    #roe=9
    if ROE > 20:
        roe_statement = "Company efficiently capital use kar rahi hai. Growth sustainable lag rahi hai."
    elif ROE > 12:
        roe_statement = "Moderate efficiency. Stable growth possible."
    else:
        roe_statement = "Low efficiency. Future growth risky ho sakti hai."
    
    roe_value=d["ROE"].tolist()
    years=d["YEAR"].tolist()
    
    current_eps = d["EPS"].iloc[-1]
    profit_growth = d["NET PROFIT"].pct_change().mean() * 100
    growth_rate = profit_growth / 100
    future_eps = current_eps * (1 + growth_rate)
    future_eps5 = current_eps * ((1 + growth_rate)**5)
    avg_pe = d["PE"].mean()
    future_price= future_eps * avg_pe
    future_price5= future_eps5 * avg_pe
    current_price = cp
    upside = round(((future_price - current_price) / current_price) * 100, 2)

    Future_statement=f"""The future price estimated for short time period is {future_price}.
for next 5years future price can grow upto {future_price5}.

The future price is calculated using the P/E method.
We estimate how much profit the company may earn per share in the future and multiply it by its average past valuation (P/E ratio).
This helps us estimate a reasonable future price based on historical performance."""
    ust="Aaj ke price se future estimated price kitna upar (ya neeche) ho sakta hai."
    # Conclusion logic
    if upside > 60:
        Statement ="The model shows very high upside potential. However, such high returns may indicate aggressive growth assumptions. In real markets, extreme valuations can lead to volatility or price corrections."
    elif upside > 25:
        Statement = "Strong upside potential. The stock appears undervalued based on earnings growth model."
    elif upside > 10:
        Statement = "Moderate upside potential. Investment may generate reasonable returns."
    else:
        Statement = "Limited upside potential. Stock may be fairly valued or slightly overvalued."
    return jsonify({
        "pnl_columns": pnl_d.columns.tolist(),
        "pnl_data": pnl_d.values.tolist(),
        "bs_columns": bs_d.columns.tolist(),
        "bs_data": bs_d.values.tolist(),
        "cf_columns": cf_d.columns.tolist(),
        "cf_data": cf_d.values.tolist(),
        "pststatement":pststatement,
        "roe":roe,"ROE":roe,
        "roe_value":roe_value,"years":years,"ust":ust,
        "cp":cp,
        "op":op,"high":high,
        "low":low,"upside":upside,"roe_statement":roe_statement,"Future_statement":Future_statement,
        "ch":ch,
        "Statement":Statement})
if __name__=="__main__":
    app.run(port=5001,debug=True)
