from sqlalchemy import Column, Integer, String, Date

from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, index=True)
    status = Column(String)


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String)
    budget = Column(Integer)
    start_date = Column(String)
    end_date = Column(String)
    