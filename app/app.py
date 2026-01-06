from fastapi import FastAPI
from stock.data_collection import company_list

app=FastAPI()

@app.get("/companies")
async def Company_list():
    return company_list