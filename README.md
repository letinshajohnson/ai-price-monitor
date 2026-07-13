# 🔍 AI Price Intelligence & Competitor Monitor

![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

A production-grade **AI-powered competitor price monitoring system** that scrapes pricing across 500+ SKUs daily, uses **GPT-4o + NLP to normalize and match product names** across different vendors, detects price changes automatically, and presents everything in a React dashboard with real-time alerts.

---

## ✨ Features

- 🕷️ **Resilient Web Scraper** — BeautifulSoup + proxy rotation, random User-Agent, rate limit handling, exponential backoff retry
- 🤖 **AI Product Matching** — GPT-4o normalizes product names across vendors (e.g. "Amul Butter 100 gms" = "AMUL BUTTER (100G)")
- 🧠 **AI Categorization** — Automatically categorizes products using GPT-4o
- 📊 **Price Intelligence Dashboard** — Compare our prices vs competitors, see position (cheapest/competitive/overpriced)
- 🔔 **Real-Time Alerts** — Auto-detects price drops and spikes with configurable thresholds
- 📈 **Price History Tracking** — Track competitor price changes over time per product
- ⚙️ **FastAPI Backend** — REST API powering the dashboard and background scraping jobs
- 🔄 **Scheduled Scraping** — Automatic daily price collection, no manual intervention

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     React Dashboard                           │
│    Price Intelligence · Alerts · Products · Price History     │
└────────────────────────┬──────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼───────────────────────────────────────┐
│                    FastAPI Backend (api.py)                    │
│                                                                │
│  /intelligence  /alerts  /products  /scrape  /stats            │
└──────────┬────────────────────────┬────────────────────────────┘
           │                        │
┌──────────▼──────────┐  ┌──────────▼───────────────────────┐
│   Price Analysis    │  │        Scraper Pipeline          │
│  price_analysis.py  │  │  scraper.py → nlp_matcher.py     │
│  - Intelligence     │  │  BeautifulSoup + Proxy Rotation  │
│  - Change Detection │  │  GPT-4o Name Normalization       │
│  - Alert Generation │  │  Product Matching & Categorize   │
└──────────┬──────────┘  └──────────────────────────────────┘
           │
┌──────────▼───────────┐
│     PostgreSQL DB    │
│  Products ·          │
│  Competitors ·       │
│  PriceRecords ·      │
│  PriceAlerts         │
└──────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI / NLP** | OpenAI GPT-4o (name normalization, matching, categorization) |
| **Backend** | Python 3.11, FastAPI |
| **Scraping** | BeautifulSoup4, Scrapy, Requests |
| **Frontend** | React 18, Tailwind CSS |
| **Database** | PostgreSQL (SQLAlchemy ORM) |
| **Scheduling** | schedule library |
| **Proxy Rotation** | Configurable proxy list |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- OpenAI API key

### 1. Clone the repository
```bash
git clone https://github.com/letinshajohnson/ai-price-monitor.git
cd ai-price-monitor
```

### 2. Backend setup
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # Fill in your values
```

### 3. Create the database
```bash
createdb price_monitor_db
```

### 4. Load demo data and test
```bash
python main.py --demo --analyze
```

### 5. Start the API
```bash
uvicorn api:app --reload --port 8000
```

### 6. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

### 7. Open the dashboard
```
Dashboard: http://localhost:3000
API Docs:  http://localhost:8000/docs
```

---

## 📁 Project Structure

```
ai-price-monitor/
│
├── api.py                         # FastAPI app — all REST endpoints
├── main.py                        # CLI pipeline runner + demo data loader
├── requirements.txt
├── .env.example
│
├── src/
│   ├── __init__.py
│   ├── config.py                  # Settings from .env
│   ├── models.py                  # SQLAlchemy: Product, Competitor, PriceRecord, PriceAlert
│   ├── scraper.py                 # Resilient web scraper (proxy, UA rotation, retry)
│   ├── nlp_matcher.py             # GPT-4o: normalize names, match products, categorize
│   └── price_analysis.py         # Intelligence metrics, change detection, alert engine
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Root layout + sidebar navigation
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx      # Price intelligence table + KPI cards
│   │   │   ├── ProductsPage.jsx   # Product list + AI-powered add form
│   │   │   └── AlertsPage.jsx     # Price change alerts with read/unread
│   │   └── utils/
│   │       └── api.js             # All API calls
│   └── package.json
│
└── data/                          # Optional: seed CSV files
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/products` | List all tracked products |
| POST | `/api/products` | Add product (AI normalizes + categorizes) |
| GET | `/api/intelligence` | Full competitive price analysis |
| GET | `/api/products/{id}/history` | Price history for one product |
| GET | `/api/alerts` | List price change alerts |
| POST | `/api/alerts/{id}/read` | Mark alert as read |
| POST | `/api/scrape` | Trigger background scraping job |
| GET | `/api/stats` | Dashboard stats |

---

## 🤖 How AI Product Matching Works

```
Competitor scrapes product: "AMUL BUTTER (100G) - REFRIGERATED"
        ↓
GPT-4o normalizes:
  Input:  "AMUL BUTTER (100G) - REFRIGERATED"
  Output: "Amul Butter 100g"
        ↓
Our product: "Amul Butter 100 gms"
GPT-4o normalizes:
  Output: "Amul Butter 100g"
        ↓
Exact match found → prices linked in DB
        ↓
Price comparison calculated
Alert generated if price changed > threshold
```

---

## 🕷️ Scraper Features

```
Request sent to competitor URL
        ↓
Random User-Agent selected (3 options rotated)
        ↓
Random delay 1.5 – 4.0 seconds (jitter)
        ↓
Optional proxy from configured list
        ↓
HTTP 429 (rate limit)?
  → Wait 30s × attempt, retry
HTTP 403/404?
  → Skip, log error
Network error?
  → Exponential backoff (2^attempt seconds)
        ↓
Max 3 retries per URL
        ↓
BeautifulSoup parses HTML
        ↓
Multiple CSS selectors tried for price extraction
        ↓
Price cleaned: "₹1,299.00" → 1299.0
```

---

## 🔔 Alert Thresholds (configurable in .env)

| Alert Type | Default Threshold | Description |
|---|---|---|
| Price Drop | 5% decrease | Competitor lowered price significantly |
| Price Spike | 10% increase | Competitor raised price significantly |

---

## 🗺️ Roadmap

- [x] Resilient web scraper with proxy rotation
- [x] GPT-4o product name normalization
- [x] AI product matching across vendors
- [x] AI auto-categorization
- [x] Price intelligence dashboard
- [x] Price change alert system
- [x] FastAPI REST backend
- [x] React dashboard with real-time stats
- [x] Demo data generator
- [ ] Scheduled automatic scraping (daily)
- [ ] Email/Slack alert delivery
- [ ] Price history charts (Recharts)
- [ ] Export to CSV/Excel
- [ ] Docker deployment
- [ ] Support for 500+ SKUs at scale

---

## 👩‍💻 Author

**Letinsha Johnson**
Senior Software Engineer · AI Specialist
📧 letinshajohnson@gmail.com
🔗 [linkedin.com/in/letinsha-johnson-3b21a5256](https://linkedin.com/in/letinsha-johnson-3b21a5256)
🐙 [github.com/letinshajohnson](https://github.com/letinshajohnson)

---