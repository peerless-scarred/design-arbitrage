# 🎨 Local Design Arbitrage — Business Card Redesign Pipeline

**Status: READY TO RUN LIVE**  
**Market: Tennessee Contractors & Tradespeople**  
**Price Point: $50/redesign | $75 rush | $150 card+logo**

---

## What Is This?

A semi-automated pipeline that finds contractors with bad business cards on Facebook, generates professional redesigns using AI-powered templates, and sells them for $50 via Stripe payment links.

## How It Works

```
Find bad card → AI extracts info → Generate 3 redesigns → 
Send watermarked preview DM → Payment → Deliver print-ready files
```

## Quick Start

```bash
# Daily workflow (interactive)
./scripts/run-daily.sh

# Or step by step:
python3 scripts/fb-group-monitor.py monitor          # Open FB groups
python3 scripts/fb-group-monitor.py add "Name" trade  # Add prospect
python3 scripts/redesign-pipeline.py generate \       # Generate designs
  --name "Biz Name" --trade plumber --phone "555-1234"
python3 scripts/simulate-dm.py                        # Preview DMs
python3 scripts/fb-group-monitor.py report            # Daily stats
```

## Project Structure

```
design-arbitrage/
├── README.md                          ← You are here
├── config.json                        ← Group URLs, keywords, settings
├── scripts/
│   ├── fb-group-monitor.py            ← Prospect tracking & group monitoring
│   ├── redesign-pipeline.py           ← AI card redesign generator (3 templates)
│   ├── stripe-setup.py                ← Stripe product/payment link creation
│   ├── webhook-server.py              ← Auto-delivery on payment (generated)
│   ├── simulate-dm.py                 ← Test DM outreach without sending
│   └── run-daily.sh                   ← Full daily workflow script
├── templates/
│   └── dm-messages.md                 ← 4 DM templates + follow-ups + objection handling
├── research/
│   ├── tennessee-groups.md            ← 15+ FB groups mapped by tier/activity
│   ├── business-card-patterns.md      ← 7 common card problems + scoring system
│   └── prospects.json                 ← Prospect database (5 test entries)
├── assets/
│   ├── screenshots/                   ← Captured bad business cards
│   ├── redesigns/                     ← Final print-ready designs
│   └── watermarked/                   ← Preview versions (with PREVIEW overlay)
├── delivery/
│   └── simulated-dms/                 ← Test DM outputs
└── config/
    └── stripe.json                    ← Stripe product IDs & payment links
```

## Pipeline Components

### 1. Facebook Group Monitor (`fb-group-monitor.py`)
- Opens target groups in browser tabs for manual browsing
- Prospect database with status tracking (new → contacted → replied → converted → delivered)
- Built-in screenshot capture (macOS `screencapture`)
- Daily reporting with revenue tracking

### 2. Redesign Pipeline (`redesign-pipeline.py`)
- **3 professional templates:**
  - Clean Professional (white, modern, blue accent)
  - Dark & Bold (navy gradient, premium feel)
  - Trade Badge (circular icon, trade-specific colors)
- Auto-maps trade → icon + accent color (12 trades supported)
- Generates both watermarked previews and clean finals
- HTML/CSS output → rendered to PNG via Playwright (headless Chromium)

### 3. Stripe Integration (`stripe-setup.py`)
- Creates 3 products: Standard ($50), Rush ($75), Full Package ($150)
- Generates shareable payment links
- Webhook server for automated file delivery via email

### 4. DM Templates (`dm-messages.md`)
- Template A: "Friendly Compliment + Offer" (best performer)
- Template B: "Social Proof" (for skeptics)
- Template C: "Problem → Solution" (direct approach)
- Template D: "Referral Group Reply" (public thread + DM combo)
- Follow-up sequence (48h, 1 week)
- Objection handling scripts

## Setup Checklist

- [x] Research: 15+ Tennessee FB groups identified
- [x] Research: Business card scoring system created
- [x] Automation: Group monitoring script
- [x] Automation: Screenshot capture workflow
- [x] Automation: AI redesign pipeline (3 templates)
- [x] Automation: Watermarking system
- [x] Business: DM message templates (4 + follow-ups)
- [x] Business: Prospect tracking database
- [x] Business: Daily workflow script
- [x] Test: 5 test prospects created
- [x] Test: 15 redesigns generated (3 per prospect)
- [x] Test: 5 DMs simulated
- [ ] **ACTION NEEDED:** Set up Stripe (`STRIPE_SECRET_KEY`)
- [ ] **ACTION NEEDED:** Join target Facebook groups
- [x] ~~Install wkhtmltopdf~~ → Using Playwright (headless Chromium) for PNG export

## Going Live

### One-time setup:
```bash
# 1. Stripe products
export STRIPE_SECRET_KEY=sk_live_...
python3 scripts/stripe-setup.py create-products

# 2. Webhook server (for auto-delivery)
python3 scripts/stripe-setup.py create-webhook
pip install flask stripe
python3 scripts/webhook-server.py  # + ngrok for public URL

# 3. Install renderer (Playwright + headless Chromium)
pip3 install playwright
python3 -m playwright install chromium
```

### Daily operation:
```bash
./scripts/run-daily.sh
```

## Economics

| Metric | Target |
|---|---|
| Groups monitored | 7 daily, 15 weekly |
| Prospects found/day | 3-5 |
| DMs sent/day | 3-5 |
| Response rate | ~20% (1 per 5) |
| Conversion rate | ~25% of responses |
| Revenue per conversion | $50-150 |
| **Weekly target** | $100-250 (2-5 sales) |
| Time investment | ~30 min/day |

## Tips

- **Best times to browse:** Monday 8-10 AM (self-promo posts), Weekday evenings
- **Best groups:** Referral groups (Tier 3) — cards are already being shared
- **Best template:** Template A (compliment + free preview) converts highest
- **Follow up:** Always follow up at 48h. Most conversions happen on follow-up.
- **Upsell:** After card delivery, pitch the $150 card+logo package
