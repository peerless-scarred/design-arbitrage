#!/usr/bin/env python3
"""
Facebook Group Monitor for Design Arbitrage
============================================
Monitors Facebook groups for business card posts and captures screenshots.

USAGE MODES:
  1. Manual mode (default): Opens groups in browser for manual scrolling
  2. Semi-auto mode: Assists with screenshot capture and filing
  3. Notification mode: Checks saved/bookmarked posts

NOTE: Facebook aggressively blocks automation. This tool is designed to
ASSIST manual browsing, not replace it. The human scrolls; the tool captures.
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime, date
from pathlib import Path

# Configuration
CONFIG_PATH = Path(__file__).parent.parent / "config.json"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "assets" / "screenshots"
PROSPECTS_FILE = Path(__file__).parent.parent / "research" / "prospects.json"

DEFAULT_CONFIG = {
    "groups": [
        {
            "name": "Nashville Contractors & Subcontractors",
            "url": "https://www.facebook.com/groups/nashvillecontractors",
            "tier": 1,
            "check_frequency": "daily"
        },
        {
            "name": "Memphis Area Contractors",
            "url": "https://www.facebook.com/groups/memphiscontractors",
            "tier": 1,
            "check_frequency": "daily"
        },
        {
            "name": "Tennessee Home Improvement & Contractors",
            "url": "https://www.facebook.com/groups/tnhomeimprovement",
            "tier": 1,
            "check_frequency": "daily"
        },
        {
            "name": "Nashville Handyman Services",
            "url": "https://www.facebook.com/groups/nashvillehandyman",
            "tier": 1,
            "check_frequency": "daily"
        },
        {
            "name": "Who Do You Recommend Nashville",
            "url": "https://www.facebook.com/groups/whodoyourecommendnashville",
            "tier": 3,
            "check_frequency": "daily"
        },
        {
            "name": "Knoxville Contractors Network",
            "url": "https://www.facebook.com/groups/knoxvillecontractors",
            "tier": 2,
            "check_frequency": "weekly"
        },
        {
            "name": "Chattanooga Home Services",
            "url": "https://www.facebook.com/groups/chattanoogahomeservices",
            "tier": 2,
            "check_frequency": "weekly"
        }
    ],
    "keywords": [
        "business card", "card", "contact", "here's my card",
        "recommend", "looking for", "need a", "know a good",
        "contractor", "handyman", "plumber", "electrician",
        "HVAC", "roofer", "painter", "landscaper"
    ],
    "screenshot_hotkey": "cmd+shift+4",  # macOS
    "check_times": ["08:00", "12:00", "17:00"]
}


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


def load_prospects():
    if PROSPECTS_FILE.exists():
        with open(PROSPECTS_FILE) as f:
            return json.load(f)
    return {"prospects": [], "stats": {"total_found": 0, "contacted": 0, "converted": 0}}


def save_prospects(data):
    PROSPECTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROSPECTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def add_prospect(name, trade, phone=None, group_source=None, card_score=None, screenshot_path=None, notes=None):
    """Add a new prospect to the database."""
    data = load_prospects()
    prospect = {
        "id": len(data["prospects"]) + 1,
        "name": name,
        "trade": trade,
        "phone": phone,
        "group_source": group_source,
        "card_score": card_score,
        "screenshot_path": screenshot_path,
        "notes": notes,
        "status": "new",  # new → contacted → replied → converted → delivered
        "found_date": date.today().isoformat(),
        "contacted_date": None,
        "converted_date": None,
        "revenue": 0
    }
    data["prospects"].append(prospect)
    data["stats"]["total_found"] += 1
    save_prospects(data)
    print(f"✅ Added prospect: {name} ({trade}) — Card score: {card_score}/10")
    return prospect


def open_groups_for_monitoring(tier=None):
    """Open Facebook groups in browser tabs for manual monitoring."""
    config = load_config()
    groups = config["groups"]
    if tier:
        groups = [g for g in groups if g["tier"] == tier]
    
    print(f"\n🔍 Opening {len(groups)} groups for monitoring...")
    print("=" * 50)
    
    for i, group in enumerate(groups):
        print(f"\n[{i+1}] {group['name']} (Tier {group['tier']})")
        print(f"    URL: {group['url']}")
        # Open in default browser
        subprocess.run(["open", group["url"]], check=False)
        if i < len(groups) - 1:
            time.sleep(2)  # Stagger tab opens
    
    print("\n" + "=" * 50)
    print("📋 MONITORING CHECKLIST:")
    print("  1. Scroll through each group's recent posts")
    print("  2. Look for business card photos")
    print("  3. Screenshot bad cards (Cmd+Shift+4 on Mac)")
    print("  4. Save screenshots to: assets/screenshots/")
    print("  5. Run: python fb-group-monitor.py add <name> <trade>")
    print("=" * 50)


def capture_screenshot(prospect_name):
    """Trigger screenshot capture and save with prospect name."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prospect_name.lower().replace(' ', '_')}_{timestamp}.png"
    filepath = SCREENSHOTS_DIR / filename
    
    print(f"\n📸 Screenshot will be saved to: {filepath}")
    print("Use Cmd+Shift+4 to capture the business card area...")
    print("(Or drag the latest screenshot to the assets/screenshots/ folder)")
    
    # On macOS, we can use screencapture
    try:
        subprocess.run(["screencapture", "-i", str(filepath)], check=True)
        print(f"✅ Screenshot saved: {filepath}")
        return str(filepath)
    except subprocess.CalledProcessError:
        print("❌ Screenshot cancelled")
        return None


def daily_report():
    """Print daily monitoring report."""
    data = load_prospects()
    today = date.today().isoformat()
    
    today_prospects = [p for p in data["prospects"] if p["found_date"] == today]
    pending = [p for p in data["prospects"] if p["status"] == "new"]
    contacted = [p for p in data["prospects"] if p["status"] == "contacted"]
    converted = [p for p in data["prospects"] if p["status"] == "converted"]
    
    print("\n" + "=" * 50)
    print(f"📊 DAILY REPORT — {today}")
    print("=" * 50)
    print(f"  Found today:     {len(today_prospects)}")
    print(f"  Total prospects:  {data['stats']['total_found']}")
    print(f"  Pending contact:  {len(pending)}")
    print(f"  Contacted:        {len(contacted)}")
    print(f"  Converted:        {len(converted)}")
    print(f"  Revenue:          ${sum(p['revenue'] for p in data['prospects'])}")
    print("=" * 50)
    
    if pending:
        print("\n🎯 READY TO CONTACT:")
        for p in pending[:5]:
            print(f"  • {p['name']} ({p['trade']}) — Score: {p['card_score']}/10 — {p['group_source']}")


def list_prospects(status=None):
    """List all prospects, optionally filtered by status."""
    data = load_prospects()
    prospects = data["prospects"]
    if status:
        prospects = [p for p in prospects if p["status"] == status]
    
    if not prospects:
        print("No prospects found.")
        return
    
    for p in prospects:
        emoji = {"new": "🆕", "contacted": "📨", "replied": "💬", "converted": "💰", "delivered": "✅"}.get(p["status"], "❓")
        print(f"  {emoji} [{p['id']}] {p['name']} ({p['trade']}) — {p['status']} — Score: {p['card_score']}/10")


def update_status(prospect_id, new_status):
    """Update a prospect's status."""
    data = load_prospects()
    for p in data["prospects"]:
        if p["id"] == prospect_id:
            old_status = p["status"]
            p["status"] = new_status
            if new_status == "contacted":
                p["contacted_date"] = date.today().isoformat()
                data["stats"]["contacted"] += 1
            elif new_status == "converted":
                p["converted_date"] = date.today().isoformat()
                p["revenue"] = 50
                data["stats"]["converted"] += 1
            save_prospects(data)
            print(f"✅ {p['name']}: {old_status} → {new_status}")
            return
    print(f"❌ Prospect #{prospect_id} not found")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Facebook Group Monitor for Design Arbitrage")
    subparsers = parser.add_subparsers(dest="command")
    
    # Monitor command
    mon = subparsers.add_parser("monitor", help="Open groups for monitoring")
    mon.add_argument("--tier", type=int, help="Only open specific tier")
    
    # Add prospect
    add = subparsers.add_parser("add", help="Add a new prospect")
    add.add_argument("name", help="Prospect name")
    add.add_argument("trade", help="Their trade/service")
    add.add_argument("--phone", help="Phone number")
    add.add_argument("--group", help="Source group")
    add.add_argument("--score", type=int, default=3, help="Card quality score (1-10, lower=worse)")
    add.add_argument("--screenshot", action="store_true", help="Capture screenshot")
    add.add_argument("--notes", help="Additional notes")
    
    # Screenshot
    ss = subparsers.add_parser("screenshot", help="Capture a screenshot")
    ss.add_argument("name", help="Prospect name for filename")
    
    # List
    ls = subparsers.add_parser("list", help="List prospects")
    ls.add_argument("--status", help="Filter by status")
    
    # Update status
    up = subparsers.add_parser("update", help="Update prospect status")
    up.add_argument("id", type=int, help="Prospect ID")
    up.add_argument("status", choices=["new", "contacted", "replied", "converted", "delivered"])
    
    # Report
    subparsers.add_parser("report", help="Daily report")
    
    args = parser.parse_args()
    
    if args.command == "monitor":
        open_groups_for_monitoring(tier=args.tier)
    elif args.command == "add":
        screenshot_path = None
        if args.screenshot:
            screenshot_path = capture_screenshot(args.name)
        add_prospect(
            name=args.name,
            trade=args.trade,
            phone=args.phone,
            group_source=args.group,
            card_score=args.score,
            screenshot_path=screenshot_path,
            notes=args.notes
        )
    elif args.command == "screenshot":
        capture_screenshot(args.name)
    elif args.command == "list":
        list_prospects(status=args.status)
    elif args.command == "update":
        update_status(args.id, args.status)
    elif args.command == "report":
        daily_report()
    else:
        parser.print_help()
        print("\n💡 Quick start: python fb-group-monitor.py monitor")


if __name__ == "__main__":
    main()
