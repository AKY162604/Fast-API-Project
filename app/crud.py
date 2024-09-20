from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from . import models, schemas

def insert_customer_item(db: Session, customer: schemas.CrmResponse):
    json_compatible_item_data = jsonable_encoder(customer)
    db_customer = models.Customer(**json_compatible_item_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def insert_marketing_data(db: Session, campaign: schemas.MarketingResponse):
    json_compatible_item_data = jsonable_encoder(campaign)
    db_campaign = models.Campaign(**json_compatible_item_data)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def get_customer(db: Session, cus_id: int):
    return db.query(models.Customer).filter(models.Customer.id == cus_id).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def get_campaign(db: Session, cam_id: int):
    return db.query(models.Campaign).filter(models.Campaign.id == cam_id).first()

def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Campaign).offset(skip).limit(limit).all()

