#!/usr/bin/env python3
"""
Simulate DM Outreach — Test the full message pipeline without sending.
Generates personalized DMs for each prospect using templates.
"""

import json
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).parent.parent
PROSPECTS_FILE = PROJECT_ROOT / "research" / "prospects.json"
DM_TEMPLATES_FILE = PROJECT_ROOT / "templates" / "dm-messages.md"
SIMULATIONS_DIR = PROJECT_ROOT / "delivery" / "simulated-dms"

# Template A (best performer)
TEMPLATE_A = """Hey {name}! 👋

Saw your post in {group} — looks like you do great {trade} work! I actually do business card and brand design for contractors here in Tennessee.

I took a few minutes and mocked up what a refreshed version of your card could look like (totally free, no strings attached). Thought you might like to see it:

📎 [ATTACHED: {preview_file}]

If you want the full print-ready files, it's just $50 and I can have them to you today. Includes 3 different design options + unlimited tweaks until you love it.

Payment link: {stripe_link}

Either way, keep crushing it! 💪"""


def load_prospects():
    with open(PROSPECTS_FILE) as f:
        return json.load(f)


def simulate_all():
    SIMULATIONS_DIR.mkdir(parents=True, exist_ok=True)
    data = load_prospects()
    
    print("\n" + "=" * 60)
    print("📨 SIMULATED DM OUTREACH")
    print(f"   Date: {date.today()}")
    print(f"   Prospects: {len(data['prospects'])}")
    print("=" * 60)
    
    stripe_link = "https://buy.stripe.com/test_XXXXXXXX"  # Replace with real link
    
    for prospect in data["prospects"]:
        if prospect["status"] != "new":
            continue
        
        safe_name = prospect["name"].lower().replace(" ", "_").replace("'", "")
        preview_file = f"{safe_name}_clean_professional_*_preview.html"
        
        # Use business name as-is (in real usage, use the owner's first name)
        display_name = prospect.get("owner_name", prospect["name"])
        dm = TEMPLATE_A.format(
            name=display_name,
            group=prospect["group_source"],
            trade=prospect["trade"],
            preview_file=preview_file,
            stripe_link=stripe_link
        )
        
        # Save simulation
        sim_file = SIMULATIONS_DIR / f"dm_{safe_name}_{date.today()}.txt"
        with open(sim_file, 'w') as f:
            f.write(f"TO: {prospect['name']} (Facebook Messenger)\n")
            f.write(f"FROM: Design Arbitrage\n")
            f.write(f"DATE: {date.today()}\n")
            f.write(f"STATUS: SIMULATED (not sent)\n")
            f.write(f"CARD SCORE: {prospect['card_score']}/10\n")
            f.write(f"NOTES: {prospect['notes']}\n")
            f.write(f"\n{'='*50}\n\n")
            f.write(dm)
            f.write(f"\n\n{'='*50}\n")
            f.write(f"ATTACHMENTS:\n")
            f.write(f"  1. {safe_name}_clean_professional_preview.html\n")
            f.write(f"  2. {safe_name}_dark_bold_preview.html\n")
            f.write(f"  3. {safe_name}_trade_badge_preview.html\n")
        
        print(f"\n{'─'*60}")
        print(f"📬 TO: {prospect['name']} ({prospect['trade']})")
        print(f"   Source: {prospect['group_source']}")
        print(f"   Card Score: {prospect['card_score']}/10")
        print(f"   Issues: {prospect['notes']}")
        print(f"{'─'*60}")
        print(dm)
        print(f"\n   💾 Saved to: {sim_file}")
    
    print(f"\n{'='*60}")
    print(f"✅ Simulated {len([p for p in data['prospects'] if p['status'] == 'new'])} DMs")
    print(f"   Files saved to: {SIMULATIONS_DIR}")
    print(f"\n   To go LIVE:")
    print(f"   1. Open each prospect's Facebook profile")
    print(f"   2. Copy the DM text above")
    print(f"   3. Attach the watermarked preview image")
    print(f"   4. Send!")
    print(f"   5. Run: python3 fb-group-monitor.py update <ID> contacted")
    print(f"{'='*60}")


if __name__ == "__main__":
    simulate_all()
