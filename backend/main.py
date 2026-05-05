import json
import os
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import or_
from sqlalchemy.orm import Session

import ai_parser
import database

load_dotenv()

app = FastAPI(title="SmartHome Catalog AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
QUOTE_CODE_PLACEHOLDERS = {"", "Bao gia", "BG-YYYYMMDD", "BG-20260420-JH"}
QUOTE_DATE_PLACEHOLDERS = {"", "dd/mm/yyyy", "20/04/2026"}


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _parse_price(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    raw = str(value).strip()
    if not raw or raw in {"-", "--"}:
        return None

    cleaned = "".join(ch for ch in raw if ch.isdigit() or ch in ".,")
    if not cleaned:
        return None

    separators = cleaned.count(".") + cleaned.count(",")
    if separators == 1:
        separator = "." if "." in cleaned else ","
        whole, fraction = cleaned.split(separator)
        if len(fraction) <= 2 and len(whole) > 3:
            try:
                return float(f"{whole}.{fraction}")
            except ValueError:
                return None

    try:
        return float(cleaned.replace(".", "").replace(",", ""))
    except ValueError:
        return None


def _normalize_uploaded_prices(item: dict, existing=None) -> dict:
    price_keys = ("list_price", "input_price", "sell_price")
    prices = []

    for key in price_keys:
        price = _parse_price(item.get(key))
        if price and price > 0:
            prices.append(price)

    distinct_prices = sorted(set(prices))
    if not distinct_prices:
        return {
            "list_price": float(getattr(existing, "list_price", 0) or 0),
            "input_price": float(getattr(existing, "input_price", 0) or 0),
            "sell_price": float(getattr(existing, "sell_price", 0) or 0),
        }

    if len(distinct_prices) == 1:
        price = distinct_prices[0]
        return {
            "list_price": price,
            "input_price": price,
            "sell_price": price,
        }

    return {
        "list_price": distinct_prices[-1],
        "input_price": distinct_prices[0],
        "sell_price": distinct_prices[1] if len(distinct_prices) >= 3 else distinct_prices[-1],
    }


def _format_quote_date(value: datetime) -> str:
    return value.strftime("%d/%m/%Y")


def _format_quote_code(value: datetime) -> str:
    return f"BG-{value.strftime('%Y%m%d')}"


def _parse_quote_created_at(value: Optional[str]) -> datetime:
    if value:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return datetime.now()


def _normalize_quote_payload(
    raw_data: str,
    created_at: Optional[datetime] = None,
    force_meta: bool = False,
) -> str:
    if not raw_data:
        return raw_data

    try:
        payload = json.loads(raw_data)
    except (TypeError, ValueError, json.JSONDecodeError):
        return raw_data

    if not isinstance(payload, dict):
        return raw_data

    outside_data = payload.get("outsideData")
    if not isinstance(outside_data, list):
        return raw_data

    while len(outside_data) < 2:
        outside_data.append("")

    created_dt = created_at or datetime.now()
    current_code = str(outside_data[0] or "").strip()
    current_date = str(outside_data[1] or "").strip()

    if force_meta or current_code in QUOTE_CODE_PLACEHOLDERS:
        outside_data[0] = _format_quote_code(created_dt)
    if force_meta or current_date in QUOTE_DATE_PLACEHOLDERS:
        outside_data[1] = _format_quote_date(created_dt)

    quote_meta = payload.get("quoteMeta")
    if not isinstance(quote_meta, dict):
        quote_meta = {}

    quote_meta["code"] = outside_data[0]
    quote_meta["date"] = outside_data[1]
    quote_meta["created_at"] = created_dt.isoformat()
    payload["quoteMeta"] = quote_meta

    return json.dumps(payload, ensure_ascii=False)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    description: str
    category: str = ""
    brand: str = ""
    image_url: str = ""
    details: str = ""
    list_price: float
    input_price: float
    sell_price: float


class ProductCreate(BaseModel):
    sku: str
    description: str = ""
    category: str = ""
    brand: str = ""
    image_url: str = ""
    details: str = ""
    list_price: float = 0.0
    input_price: float = 0.0
    sell_price: float = 0.0


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    image_url: Optional[str] = None
    details: Optional[str] = None
    list_price: Optional[float] = None
    input_price: Optional[float] = None
    sell_price: Optional[float] = None


class LoginRequest(BaseModel):
    password: str


class QuoteBase(BaseModel):
    customer_name: str
    data: str


class QuoteCreate(QuoteBase):
    pass


class QuoteUpdate(QuoteBase):
    pass


class QuoteResponse(QuoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: str


@app.post("/api/auth/login")
def admin_login(req: LoginRequest):
    if not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=503,
            detail="ADMIN_PASSWORD chưa được cấu hình trong file .env",
        )
    if req.password == ADMIN_PASSWORD:
        return {"status": "success", "token": "authenticated"}
    raise HTTPException(status_code=401, detail="Sai mật khẩu")


@app.get("/admin")
def serve_admin():
    admin_path = os.path.join(os.path.dirname(__file__), "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Trang admin không tồn tại")


PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@app.get("/baogia")
def serve_baogia():
    path = os.path.join(PARENT_DIR, "Bao_Gia_Jay_Home_Truc_Quan.html")
    if os.path.exists(path):
        return FileResponse(path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Trang báo giá không tồn tại")


@app.get("/assets/company-logo")
def serve_company_logo():
    path = os.path.join(PARENT_DIR, "Asset-14logo-khoa-duy-blackok-1024x461.png")
    if os.path.exists(path):
        return FileResponse(path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo công ty không tồn tại")


@app.get("/Asset-14logo-khoa-duy-blackok-1024x461.png")
def serve_company_logo_legacy_path():
    return serve_company_logo()


@app.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    """Lấy danh sách các danh mục duy nhất."""
    results = db.query(database.Product.category).distinct().all()
    cats = [r[0] for r in results if r[0]]
    return sorted(cats)


@app.get("/api/products", response_model=List[ProductResponse])
def list_all_products(db: Session = Depends(get_db)):
    """Lấy toàn bộ danh sách sản phẩm cho trang admin."""
    return db.query(database.Product).order_by(database.Product.id.desc()).all()


@app.get("/api/search", response_model=List[ProductResponse])
def search_products(q: str = "", db: Session = Depends(get_db)):
    if len(q) < 1:
        return db.query(database.Product).limit(50).all()
    search_pattern = f"%{q}%"
    products = (
        db.query(database.Product)
        .filter(
            or_(
                database.Product.sku.ilike(search_pattern),
                database.Product.description.ilike(search_pattern),
            )
        )
        .limit(20)
        .all()
    )
    return products


@app.post("/api/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(database.Product).filter(database.Product.sku == product.sku).first()
    if db_product:
        raise HTTPException(status_code=400, detail="SKU đã tồn tại")
    new_prod = database.Product(**product.model_dump())
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod


@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Cập nhật thông tin sản phẩm theo ID."""
    db_product = db.query(database.Product).filter(database.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")

    update_data = product.model_dump(exclude_unset=True)
    if "sku" in update_data and update_data["sku"] != db_product.sku:
        existing = (
            db.query(database.Product)
            .filter(database.Product.sku == update_data["sku"])
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="SKU mới đã tồn tại")

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Xóa sản phẩm theo ID."""
    db_product = db.query(database.Product).filter(database.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    db.delete(db_product)
    db.commit()
    return {"status": "success", "message": f"Đã xóa sản phẩm ID {product_id}"}


@app.post("/api/quotes", response_model=QuoteResponse)
def create_quote(quote: QuoteCreate, db: Session = Depends(get_db)):
    db_quote = database.Quote(
        customer_name=quote.customer_name,
        created_at=datetime.now().isoformat(),
        data=quote.data,
    )
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote


@app.get("/api/quotes", response_model=List[QuoteResponse])
def get_quotes(db: Session = Depends(get_db)):
    return db.query(database.Quote).order_by(database.Quote.id.desc()).all()


@app.get("/api/quotes/{quote_id}", response_model=QuoteResponse)
def get_quote(quote_id: int, db: Session = Depends(get_db)):
    db_quote = db.query(database.Quote).filter(database.Quote.id == quote_id).first()
    if not db_quote:
        raise HTTPException(status_code=404, detail="KhÃ´ng tÃ¬m tháº¥y bÃ¡o giÃ¡")
    return db_quote


@app.put("/api/quotes/{quote_id}", response_model=QuoteResponse)
def update_quote(quote_id: int, quote: QuoteUpdate, db: Session = Depends(get_db)):
    db_quote = db.query(database.Quote).filter(database.Quote.id == quote_id).first()
    if not db_quote:
        raise HTTPException(status_code=404, detail="KhÃ´ng tÃ¬m tháº¥y bÃ¡o giÃ¡")
    db_quote.customer_name = quote.customer_name
    db_quote.data = quote.data
    db.commit()
    db.refresh(db_quote)
    return db_quote


@app.post("/api/quotes/{quote_id}/duplicate", response_model=QuoteResponse)
def duplicate_quote(quote_id: int, db: Session = Depends(get_db)):
    db_quote = db.query(database.Quote).filter(database.Quote.id == quote_id).first()
    if not db_quote:
        raise HTTPException(status_code=404, detail="KhÃ´ng tÃ¬m tháº¥y bÃ¡o giÃ¡")
    new_quote = database.Quote(
        customer_name=f"{db_quote.customer_name} - Copy",
        created_at=datetime.now().isoformat(),
        data=db_quote.data,
    )
    db.add(new_quote)
    db.commit()
    db.refresh(new_quote)
    return new_quote


@app.delete("/api/quotes/{quote_id}")
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    db_quote = db.query(database.Quote).filter(database.Quote.id == quote_id).first()
    if not db_quote:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo giá")
    db.delete(db_quote)
    db.commit()
    return {"status": "success", "message": f"Đã xóa báo giá ID {quote_id}"}


@app.post("/api/upload")
async def upload_catalog(
    file: UploadFile = File(...),
    brand: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    try:
        extracted_items = await ai_parser.parse_file(file_location, file.filename)

        count = 0
        for item in extracted_items:
            sku_val = str(item.get("sku", "")).strip()
            if not sku_val:
                continue

            final_brand = brand if brand else str(item.get("brand", ""))

            existing = db.query(database.Product).filter(database.Product.sku == sku_val).first()
            prices = _normalize_uploaded_prices(item, existing)
            if existing:
                existing.description = item.get("description", existing.description)
                existing.category = item.get("category", existing.category) or existing.category
                existing.brand = final_brand or existing.brand
                existing.image_url = item.get("image_url", existing.image_url) or existing.image_url
                existing.details = item.get("details", existing.details) or existing.details
                existing.list_price = prices["list_price"]
                existing.input_price = prices["input_price"]
                existing.sell_price = prices["sell_price"]
            else:
                new_prod = database.Product(
                    sku=sku_val,
                    description=str(item.get("description", "")),
                    category=str(item.get("category", "")),
                    brand=final_brand,
                    image_url=str(item.get("image_url", "")),
                    details=str(item.get("details", "")),
                    list_price=prices["list_price"],
                    input_price=prices["input_price"],
                    sell_price=prices["sell_price"],
                )
                db.add(new_prod)
            count += 1

        db.commit()
        return {
            "status": "success",
            "message": f"Đã bóc tách AI và lưu {count} sản phẩm vào cơ sở dữ liệu.",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
