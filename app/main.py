from fastapi import FastAPI

app = FastAPI(title="Finance Planner API")

@app.get("/")
async def root():
    return {"message": "API Financeira iniciada com FastAPI!"}
