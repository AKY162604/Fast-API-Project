from .celery import app
from sqlalchemy.orm import Session
from .crud import insert_customer_item, insert_marketing_data
from .database import get_db
from contextlib import contextmanager


@app.task
def insert_customer(customer_data):
    with contextmanager(get_db)() as db:
        for cus in customer_data:
            cus1 = insert_customer_item(db, cus)
    

@app.task
def insert_campaigns(campaigns_data):
    with contextmanager(get_db)() as db:
        for cam in campaigns_data:
            camp = insert_marketing_data(db, cam)
        