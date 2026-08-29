import psycopg2
import os
import logging
from psycopg2 import pool
from dotenv import load_dotenv

_pool=None
load_dotenv()
DB_url = os.getenv("NEON_DATABASE_URL")
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

def execute_query(cursor,filePath):
    with open(filePath,'r',encoding="UTF-8") as sql_file:
        print(f"calling the path : {filePath}")
        query=sql_file.read()
        cursor.execute(query)

def create_orders_table():
    logger.info("creation Orders Table")
    _pool=get_pool_conn()
    conn=_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS material_order_status ")
            logger.info("Dropped the Table material_order_status  if exists")
            base_dir = os.path.dirname(__file__)
            schema_path = os.path.join(base_dir,"migration","01_schema.sql")
            data_path = os.path.join(base_dir,"migration","02_seed_data.sql")
            logger.info("Schema and seed_data Collected")
            print(schema_path)
            print(data_path)
            execute_query(cur,schema_path)
            logger.info("Created the table material_order_status")
            execute_query(cur,data_path)
            logger.info("Added the Data Succesfully to the table")
            conn.commit()
    except Exception:
        logger.exception("Error during Table creation")
    finally:
        _pool.putconn(conn)
        
def add_new_order(order_details:dict):
    _pool=get_pool_conn()
    conn = _pool.getconn()
    insert_query_path = os.path.join(os.path.dirname('__file__'),"migartion","03_insert_record.sql")
    with open(insert_query_path,'r',encoding="UTF-8") as read_file:
        query=read_file.read()
    try:
        with conn.cursor() as cur:
            conn.execute(query,order_details)
            conn.commit()
            logger.info("Record Inserted Successfully")
    except Exception:
        logger.exception("Error occured while inserting Record")
    finally:
        _pool.putconn(conn)


if __name__=="__main__":
    create_orders_table()
