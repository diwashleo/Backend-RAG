from fastapi import FastAPI
import uvicorn
from core.db import init_db
from routers import ingestion, rag

# Create tables
init_db()

app = FastAPI(title="File Upload API")

app.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])
app.include_router(rag.router, prefix="/rag", tags=["rag"])

if __name__=="__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000, reload=True)