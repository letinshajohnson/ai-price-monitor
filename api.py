from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.models import init_db, get_db, Product, Competitor, PriceRecord, PriceAlert
from src.price_analysis import (get_latest_prices, get_price_history,
                                  compute_price_intelligence, detect_price_changes)
from src.nlp_matcher import normalize_product_name, categorize_product
from pydantic import BaseModel
from datetime import datetime
import uuid, pandas as pd

init_db()

app = FastAPI(title="AI Price Intelligence API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


# ── Products ─────────────────────────────────────────────────────────────────
class ProductIn(BaseModel):
    name: str
    our_price: float
    category: str = None

@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    return [{"id": p.id, "name": p.name, "our_price": p.our_price,
             "category": p.category} for p in db.query(Product).all()]

@app.post("/api/products")
def add_product(data: ProductIn, db: Session = Depends(get_db)):
    normalized = normalize_product_name(data.name)
    category   = data.category or categorize_product(data.name)
    product    = Product(id=str(uuid.uuid4()), name=data.name,
                         normalized_name=normalized, category=category,
                         our_price=data.our_price)
    db.add(product); db.commit()
    return {"id": product.id, "normalized_name": normalized, "category": category}


# ── Intelligence ──────────────────────────────────────────────────────────────
@app.get("/api/intelligence")
def price_intelligence(db: Session = Depends(get_db)):
    df = get_latest_prices(db)
    if df.empty:
        return {"data": [], "summary": {}}
    intel = compute_price_intelligence(df)
    summary = {
        "total_products":   len(intel),
        "cheapest":         len(intel[intel["position"] == "✅ Cheapest"]),
        "competitive":      len(intel[intel["position"] == "🟡 Competitive"]),
        "overpriced":       len(intel[intel["position"] == "🔴 Overpriced"]),
        "avg_price_gap":    round(intel["price_gap_pct"].mean(), 1)
    }
    return {"data": intel.to_dict("records"), "summary": summary}

@app.get("/api/products/{product_id}/history")
def price_history(product_id: str, days: int = 30, db: Session = Depends(get_db)):
    df = get_price_history(db, product_id, days)
    return df.to_dict("records") if not df.empty else []


# ── Alerts ────────────────────────────────────────────────────────────────────
@app.get("/api/alerts")
def get_alerts(unread_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(PriceAlert)
    if unread_only:
        query = query.filter(PriceAlert.is_read == False)
    alerts = query.order_by(PriceAlert.created_at.desc()).limit(50).all()
    return [{
        "id": a.id, "type": a.alert_type, "message": a.message,
        "old_price": a.old_price, "new_price": a.new_price,
        "change_pct": a.change_pct, "competitor": a.competitor,
        "product": a.product.name, "created_at": a.created_at, "is_read": a.is_read
    } for a in alerts]

@app.post("/api/alerts/{alert_id}/read")
def mark_read(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(PriceAlert).filter(PriceAlert.id == alert_id).first()
    if alert:
        alert.is_read = True; db.commit()
    return {"ok": True}

@app.post("/api/scrape")
def trigger_scrape(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger a background scraping job."""
    background_tasks.add_task(detect_price_changes, db)
    return {"message": "Scraping job triggered"}

@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "total_products":   db.query(Product).count(),
        "total_competitors":db.query(Competitor).count(),
        "total_prices":     db.query(PriceRecord).count(),
        "unread_alerts":    db.query(PriceAlert).filter(PriceAlert.is_read == False).count(),
    }
