import json
import re
from openai import OpenAI
from src.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


def normalize_product_name(name: str) -> str:
    """
    Use GPT-4o to normalize a product name to a canonical form.
    e.g. 'Amul Butter 100 gms' and 'AMUL BUTTER (100G)' → 'Amul Butter 100g'
    Falls back to basic string normalization if API fails.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Normalize this product name to a clean, canonical form.
Remove extra spaces, fix capitalization, standardize units (gm→g, ml→ml, kg→kg, ltr→L).
Return ONLY the normalized name, nothing else.

Product name: {name}"""
            }],
            max_tokens=50,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return _basic_normalize(name)


def _basic_normalize(name: str) -> str:
    """Fallback: basic string normalization without API."""
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"(\d+)\s*(gms?|grm?)", r"\1g",  name)
    name = re.sub(r"(\d+)\s*(ltr?|litre?)", r"\1L", name)
    name = re.sub(r"(\d+)\s*(ml)",          r"\1ml", name)
    name = re.sub(r"(\d+)\s*(kgs?)",        r"\1kg", name)
    return name.title()


def match_products_with_ai(
    our_products: list[str],
    competitor_products: list[str]
) -> list[dict]:
    """
    Use GPT-4o to match our products to competitor products across different naming conventions.
    Returns list of {our_product, competitor_product, confidence} dicts.
    """
    if not our_products or not competitor_products:
        return []

    prompt = f"""Match each product from "Our Products" to the most similar product in "Competitor Products".
Only match if you are confident they are the same or equivalent product.

Our Products:
{json.dumps(our_products, indent=2)}

Competitor Products:
{json.dumps(competitor_products, indent=2)}

Return ONLY a JSON array of matches. Each match: {{"our_product": "...", "competitor_product": "...", "confidence": 0.0-1.0}}
Only include matches with confidence >= 0.7. Return [] if no confident matches."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception:
        return []


def categorize_product(name: str) -> str:
    """Use GPT-4o to categorize a product name into a standard category."""
    categories = ["Dairy", "Grains & Cereals", "Beverages", "Personal Care",
                  "Household", "Snacks", "Oils & Fats", "Spices", "Fruits & Vegetables", "Other"]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Categorize this product into one of these categories:
{', '.join(categories)}

Product: {name}
Reply with ONLY the category name."""
            }],
            max_tokens=20,
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        return result if result in categories else "Other"
    except Exception:
        return "Other"
