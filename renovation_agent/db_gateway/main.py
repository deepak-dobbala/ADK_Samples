import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
import logging

_pool=None
load_dotenv()
DB_url = os.getenv("NEON_DATABASE_URL")
logging.info("Calling the pooling Connection to DB")
logger = logging.getLogger(__name__)
def get_pool_conn():
    global _pool
    try:
        if _pool is None:
            _pool = psycopg2.pool.SimpleConnectionPool(1,5,DB_url,sslmode="require")
            logger.info("The Pooling connection to the DB established")
        return _pool
    except Exception:
        logger.exception("Error Occured while establishing connection")
        raise

get_pool_conn()