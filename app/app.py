import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from stock.data_collection import company_list
from app.model import stock_request
from stock.data_collection import analyze_stock, build_summary, compare_summaries

def clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(i) for i in obj]
    return obj


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/companies")
async def Company_list():
    return company_list


@app.post("/data")
async def get_stock_analysis(request:stock_request):
    df=analyze_stock(request.symbol)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="Stock data not found")
    data=df.tail(30).reset_index().to_dict(orient="records")
    cleaned_data=clean_nan(data)
    return cleaned_data

@app.get("/summary/{symbol}")
async def get_summary(symbol: str):
    df = analyze_stock(symbol)

    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No data found")

    return build_summary(df, symbol)


@app.get("/compare/{symbol1}/{symbol2}")
async def compare_stocks(symbol1: str, symbol2: str):
    df1 = analyze_stock(symbol1)
    df2 = analyze_stock(symbol2)

    if df1 is None or df1.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol1}")

    if df2 is None or df2.empty:
        raise HTTPException(status_code=404, detail=f"No data for {symbol2}")

    summary1 = build_summary(df1, symbol1)
    summary2 = build_summary(df2, symbol2)

    comparison = compare_summaries(summary1, summary2)

    return {
        "stock_1": summary1,
        "stock_2": summary2,
        "comparison": comparison
    }
