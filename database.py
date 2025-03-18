# type: ignore

from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./jeepneys.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # needed for SQLite in a single thread
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Jeepney(Base):
    __tablename__ = "jeepneys"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    popup = Column(String, nullable=True)

# Create the tables if they don't exist yet
Base.metadata.create_all(bind=engine)