from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./catalog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    description = Column(String)
    category = Column(String, default="")
    brand = Column(String, default="")
    image_url = Column(String, default="")
    details = Column(String, default="")
    list_price = Column(Float, default=0.0)
    input_price = Column(Float, default=0.0)
    sell_price = Column(Float, default=0.0)


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    created_at = Column(String)  # Lưu dạng ISO string cho đơn giản với SQLite
    data = Column(String)  # Dữ liệu dạng JSON string


Base.metadata.create_all(bind=engine)
