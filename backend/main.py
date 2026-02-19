from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

from dotenv import load_dotenv

from routers import mandate_ledger

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mandate_ledger.router)

router = APIRouter()

@app.get("/")
async def read_root(request: Request):
    return {"message":"Server is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "message": "Backend service is running"
    }