import logging
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.cache import (
    get_cached_product,
    invalidate_product_cache,
    is_redis_ready,
    set_cached_product,
    wait_for_redis,
)
from app.database import get_db, init_db, is_database_ready
from app.logging_config import RequestIdMiddleware, configure_logging
from app.metrics import setup_metrics
from app.models import Product
from app.schemas import ProductCreate, ProductPatch, ProductResponse, ProductStockUpdate


configure_logging()
logger = logging.getLogger("product-service")

app = FastAPI(title="product-service", version="1.0.0")
app.add_middleware(RequestIdMiddleware)
setup_metrics(app)


@app.on_event("startup")
def startup() -> None:
    init_db()
    wait_for_redis()
    logger.info("service_started", extra={"event": "service.started"})


def product_to_cache_payload(product: Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "currency": product.currency,
        "stock": product.stock,
        "status": product.status,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "product-service"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if not is_database_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database is not ready")
    if not is_redis_ready():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="redis is not ready")
    return {"status": "ready", "service": "product-service"}


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    invalidate_product_cache(product.id)
    logger.info("product_created", extra={"event": "product.created"})
    return product


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, response: Response, db: Session = Depends(get_db)) -> Product | dict[str, Any]:
    cached = get_cached_product(product_id)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        logger.info("product_cache_hit", extra={"event": "product.cache_hit", "cache": "hit"})
        return cached

    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")

    response.headers["X-Cache"] = "MISS"
    set_cached_product(product_id, product_to_cache_payload(product))
    logger.info("product_cache_miss", extra={"event": "product.cache_miss", "cache": "miss"})
    return product


@app.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    return list(db.query(Product).order_by(Product.created_at.desc()).all())


@app.patch("/products/{product_id}", response_model=ProductResponse)
def patch_product(product_id: str, payload: ProductPatch, db: Session = Depends(get_db)) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    invalidate_product_cache(product_id)
    logger.info("product_updated", extra={"event": "product.updated"})
    return product


@app.patch("/products/{product_id}/stock", response_model=ProductResponse)
def update_product_stock(product_id: str, payload: ProductStockUpdate, db: Session = Depends(get_db)) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")

    product.stock = payload.stock
    db.commit()
    db.refresh(product)
    invalidate_product_cache(product_id)
    logger.info("product_stock_updated", extra={"event": "product.stock_updated"})
    return product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)) -> Response:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product not found")

    product.status = "archived"
    db.commit()
    invalidate_product_cache(product_id)
    logger.info("product_archived", extra={"event": "product.archived"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
