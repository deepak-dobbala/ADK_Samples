from dotenv import load_dotenv
import os
import logging
from psycopg2 import pool
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Depends,Header


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.getenv('NEON_DATABASE_URL')
GATEWAY_API_KEY = os.getenv('GATEWAY_API_KEY')
_pool: pool.ThreadConnectionPool | None = None

@asynccontextmanager
async def lifetime(app: FastAPI):
    global _pool
    _pool = pool.ThreadConnectionPool(minconn=1, maxconn=10, dsn=DB_URL)
    logger.info("Database connection pool created")
    yield
    if _pool:
        _pool.closeall()
        logger.info("Database connection pool closed")

app=FastAPI(lifespan=lifetime,title="DB Gateway",description="A gateway for the database")

def verify_api_key(api_key: str = Header(...)):
    if api_key != GATEWAY_API_KEY:
        HTTPException(status_code=401, detail="Invalid API key")
