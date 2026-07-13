import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.models import PriceRecord, PriceAlert, Product
from src.config import PRICE_DROP_ALERT_THRESHOLD, PRICE_SPIKE_ALERT_THRESHOLD
import uuid


def get_latest_prices(db: Session) -> pd.DataFrame:
    """Get most recent price per product per competitor."""
    records = db.query(PriceRecord).all()
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame([{
        "product_id":   r.product_id,
        "product_name": r.product.name,
        "category":     r.product.category,
        "our_price":    r.product.our_price,
        "competitor":   r.competitor.name,
        "price":        r.price,
        "scraped_at":   r.scraped_at
    } for r in records])

    # Keep only the latest price per product-competitor pair
    df = df.sort_values("scraped_at").groupby(
        ["product_id", "competitor"]
    ).last().reset_index()

    return df


def get_price_history(db: Session, product_id: str, days: int = 30) -> pd.DataFrame:
    """Get price history for a product over N days."""
    cutoff  = datetime.utcnow() - timedelta(days=days)
    records = db.query(PriceRecord).filter(
        PriceRecord.product_id == product_id,
        PriceRecord.scraped_at >= cutoff
    ).order_by(PriceRecord.scraped_at).all()

    return pd.DataFrame([{
        "date":       r.scraped_at,
        "competitor": r.competitor.name,
        "price":      r.price
    } for r in records])


def compute_price_intelligence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute competitive intelligence metrics per product:
    - min/max/avg competitor price
    - price vs our price
    - position (cheapest/priciest/competitive)
    - price gap %
    """
    if df.empty:
        return df

    agg = df.groupby(["product_id", "product_name", "category", "our_price"]).agg(
        min_competitor_price = ("price", "min"),
        max_competitor_price = ("price", "max"),
        avg_competitor_price = ("price", "mean"),
        num_competitors      = ("competitor", "nunique"),
        cheapest_competitor  = ("competitor", lambda x: x[df.loc[x.index, "price"].idxmin()]),
    ).reset_index()

    agg["our_price"]           = agg["our_price"].fillna(0)
    agg["price_gap_pct"]       = ((agg["our_price"] - agg["min_competitor_price"])
                                   / agg["min_competitor_price"] * 100).round(1)
    agg["vs_avg_pct"]          = ((agg["our_price"] - agg["avg_competitor_price"])
                                   / agg["avg_competitor_price"] * 100).round(1)

    def position(row):
        if row["our_price"] <= row["min_competitor_price"]:
            return "✅ Cheapest"
        elif row["our_price"] <= row["avg_competitor_price"]:
            return "🟡 Competitive"
        else:
            return "🔴 Overpriced"

    agg["position"] = agg.apply(position, axis=1)
    return agg


def detect_price_changes(db: Session) -> list[dict]:
    """
    Compare today's prices to yesterday's and generate change alerts.
    Returns list of alert dicts.
    """
    now       = datetime.utcnow()
    today     = now - timedelta(hours=26)
    yesterday = now - timedelta(hours=50)

    today_records = db.query(PriceRecord).filter(
        PriceRecord.scraped_at >= today
    ).all()
    yesterday_records = db.query(PriceRecord).filter(
        PriceRecord.scraped_at >= yesterday,
        PriceRecord.scraped_at < today
    ).all()

    if not today_records or not yesterday_records:
        return []

    today_map = {(r.product_id, r.competitor_id): r.price for r in today_records}
    yest_map  = {(r.product_id, r.competitor_id): r.price for r in yesterday_records}

    alerts = []
    for key, new_price in today_map.items():
        if key not in yest_map:
            continue
        old_price  = yest_map[key]
        change_pct = ((new_price - old_price) / old_price * 100) if old_price else 0

        if abs(change_pct) < 1:
            continue

        product    = db.query(Product).filter(Product.id == key[0]).first()
        competitor = next((r.competitor for r in today_records
                          if r.product_id == key[0] and r.competitor_id == key[1]), None)

        if not product or not competitor:
            continue

        if change_pct <= -PRICE_DROP_ALERT_THRESHOLD:
            alert_type = "drop"
            message    = (f"{competitor.name} dropped price of {product.name} "
                         f"by {abs(change_pct):.1f}% (₹{old_price:.0f} → ₹{new_price:.0f})")
        elif change_pct >= PRICE_SPIKE_ALERT_THRESHOLD:
            alert_type = "spike"
            message    = (f"{competitor.name} raised price of {product.name} "
                         f"by {change_pct:.1f}% (₹{old_price:.0f} → ₹{new_price:.0f})")
        else:
            continue

        alert = PriceAlert(
            id=str(uuid.uuid4()),
            product_id=product.id,
            alert_type=alert_type,
            message=message,
            old_price=old_price,
            new_price=new_price,
            change_pct=round(change_pct, 1),
            competitor=competitor.name
        )
        db.add(alert)
        alerts.append({"type": alert_type, "message": message})

    db.commit()
    return alerts
