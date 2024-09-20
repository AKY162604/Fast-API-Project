from math import ceil
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
from fastapi import status
import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from . import crud, models, schemas, tasks
from .database import SessionLocal, engine, get_db


import requests

models.Base.metadata.create_all(bind=engine)

REDIS_URL = "redis://127.0.0.1:6379"


async def service_name_identifier(request: Request):
    service = request.headers.get("Service-Name")
    return service


async def custom_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(pexpire / 1000)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too Many Requests. Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_connection = redis.from_url(REDIS_URL, encoding="utf8")
    await FastAPILimiter.init(
        redis=redis_connection,
        identifier=service_name_identifier,
        http_callback=custom_callback,
    )
    yield
    await FastAPILimiter.close()

app = FastAPI(lifespan=lifespan)

# External CRM API endpoint
EXTERNAL_CRM_API = "https://challenge.berrydev.ai/api/crm/customers"

# External Marketing API endpoint
EXTERNAL_Marketing_API = "https://challenge.berrydev.ai/api/marketing/campaigns"


# Cache to store recent API responses
cache = {}





@app.get("/external-crm-data")
async def get_crm_data(
    offset: int = 0,
    limit: int = 100,
    api_key: str = None,
):
    try:
        # Prepare headers
        headers = {}
        if api_key:
            headers["X-API-Key"] = f"{api_key}"

        # Make API request
        params = {
            "offset": offset,
            "limit": limit
        }

        response = requests.get(EXTERNAL_CRM_API, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Process the data (e.g., convert to CrmResponse objects)
            processed_data = [
                schemas.CrmResponse(**item) for item in data["customers"]
            ]
            tasks.insert_customer.delay(data["customers"])
            return {"customers": processed_data, "total": data["total"], "offset":data["offset"], "limit": data["limit"]}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Error: {response.text}")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@app.get("/external-marketing-data")
async def get_marketing_data(
    offset: int = 0,
    limit: int = 100,
    api_key: str = None,
):
    try:
        # Prepare headers
        headers = {}
        if api_key:
            headers["X-API-Key"] = f"{api_key}"

        # Make API request
        params = {
            "offset": offset,
            "limit": limit
        }

        response = requests.get(EXTERNAL_Marketing_API, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(data)
            
            # Process the data (e.g., convert to CrmResponse objects)
            processed_data = [
                schemas.MarketingResponse(**item) for item in data["campaigns"]
            ]
            tasks.insert_campaigns.delay(data["campaigns"])
            return {"campaigns": processed_data, "total": len(data["campaigns"])}
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Error: {response.text}")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/customer/{cus_id}", response_model=schemas.CrmResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_customer(cus_id: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db, cus_id=cus_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@app.get("/customers/", response_model=list[schemas.CrmResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_all_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, skip=skip, limit=limit)
    return customers

@app.get("/campaigns{cam_id}", response_model=schemas.MarketingResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_campaign(cam_id: int, db: Session = Depends(get_db)):
    db_campaigns = crud.get_campaign(db, cam_id=cam_id)
    if db_campaigns is None:
        raise HTTPException(status_code=404, detail="Campaigns not found")
    return db_campaigns

@app.get("/campaigns/", response_model=list[schemas.MarketingResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_all_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    campaigns = crud.get_campaigns(db, skip=skip, limit=limit)
    return campaigns