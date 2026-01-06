import math
from fastapi import FastAPI, HTTPException
from stock.data_collection import company_list
from app.model import stock_request
from stock.data_collection import analyze_stock

def clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(i) for i in obj]
    return obj


app=FastAPI()

@app.get("/companies")
async def Company_list():
    return company_list


@app.post("/analyze_stock")
async def get_stock_analysis(request:stock_request):
    df=analyze_stock(request.symbol)
    if df is None or df.empty:
        return HTTPException(status_code=404, detail="Stock data not found")
    data=df.tail(30).reset_index().to_dict(orient="records")
    cleaned_data=clean_nan(data)
    return cleaned_data