"""
AI Price Intelligence Monitor — Main Pipeline
Run: python main.py [--demo] [--product "Rice 5kg"]
"""
import argparse
from datetime import datetime
from src.models import init_db, SessionLocal, Product, Competitor, PriceRecord
from src.scraper import Scraper
from src.nlp_matcher import normalize_product_name, match_products_with_ai
from src.price_analysis import (get_latest_prices, compute_price_intelligence,
                                  detect_price_changes)
import uuid
import random


def run_demo():
    """Populate DB with demo data to showcase the system."""
    print("\n🎭 Loading demo data...")
    db = SessionLocal()

    # Add demo products
    demo_products = [
        ("Amul Butter 100g",       55.0,  "Dairy"),
        ("Tata Salt 1kg",          20.0,  "Essentials"),
        ("Fortune Sunflower Oil 1L",120.0, "Oils & Fats"),
        ("Aashirvaad Atta 5kg",    260.0, "Grains & Cereals"),
        ("Surf Excel 1kg",         185.0, "Household"),
        ("Dove Shampoo 180ml",      90.0, "Personal Care"),
    ]

    product_objs = []
    for name, price, cat in demo_products:
        existing = db.query(Product).filter(Product.name == name).first()
        if not existing:
            p = Product(id=str(uuid.uuid4()), name=name, our_price=price, category=cat,
                        normalized_name=normalize_product_name(name))
            db.add(p)
            product_objs.append(p)
        else:
            product_objs.append(existing)

    # Add demo competitors
    demo_competitors = ["BigBasket", "Blinkit", "Zepto", "JioMart"]
    comp_objs = []
    for name in demo_competitors:
        existing = db.query(Competitor).filter(Competitor.name == name).first()
        if not existing:
            c = Competitor(id=str(uuid.uuid4()), name=name,
                           base_url=f"https://{name.lower()}.com")
            db.add(c)
            comp_objs.append(c)
        else:
            comp_objs.append(existing)

    db.commit()
    db.refresh(product_objs[0]) if product_objs else None

    # Add demo price records
    for product in db.query(Product).all():
        for competitor in db.query(Competitor).all():
            variation = random.uniform(0.85, 1.15)
            price = round((product.our_price or 100) * variation, 2)
            record = PriceRecord(
                id=str(uuid.uuid4()),
                product_id=product.id,
                competitor_id=competitor.id,
                price=price,
                url=f"https://{competitor.name.lower()}.com/{product.name.lower().replace(' ','-')}"
            )
            db.add(record)

    db.commit()
    print(f"✅ Demo data loaded: {db.query(Product).count()} products, "
          f"{db.query(Competitor).count()} competitors, "
          f"{db.query(PriceRecord).count()} price records")
    db.close()


def run_analysis():
    """Run full price intelligence analysis and print results."""
    print("\n📊 Running price intelligence analysis...")
    db = SessionLocal()

    df    = get_latest_prices(db)
    if df.empty:
        print("⚠️  No price data found. Run with --demo first.")
        db.close()
        return

    intel = compute_price_intelligence(df)

    print(f"\n{'Product':<30} {'Our Price':>10} {'Min Competitor':>15} {'Gap %':>8} {'Position'}")
    print("-" * 75)
    for _, row in intel.iterrows():
        print(f"{row['product_name']:<30} "
              f"₹{row['our_price']:>8.0f} "
              f"₹{row['min_competitor_price']:>12.0f} "
              f"{row['price_gap_pct']:>7.1f}% "
              f"{row['position']}")

    cheapest   = len(intel[intel["position"] == "✅ Cheapest"])
    overpriced = len(intel[intel["position"] == "🔴 Overpriced"])
    print(f"\n📌 Summary: {cheapest} cheapest | {overpriced} overpriced | {len(intel)} total products")

    # Check for new price change alerts
    alerts = detect_price_changes(db)
    if alerts:
        print(f"\n🔔 {len(alerts)} new price alerts:")
        for a in alerts[:5]:
            print(f"   [{a['type'].upper()}] {a['message']}")

    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Price Intelligence Monitor")
    parser.add_argument("--demo",    action="store_true", help="Load demo data")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    args = parser.parse_args()

    init_db()

    if args.demo:
        run_demo()
    if args.analyze or args.demo:
        run_analysis()
