#!/usr/bin/env python3
"""
AI Business Card Redesign Pipeline
====================================
Takes a screenshot of a bad business card, extracts info via AI vision,
and generates a professional redesign using HTML/CSS templates.

Pipeline: Screenshot → AI Extract → Template Fill → Render → Watermark → Deliver
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from string import Template

PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "assets" / "redesigns"
WATERMARK_DIR = PROJECT_ROOT / "assets" / "watermarked"

# Ensure dirs exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
WATERMARK_DIR.mkdir(parents=True, exist_ok=True)


# ─── HTML/CSS Card Templates ───────────────────────────────────────────

CARD_TEMPLATES = {
    "clean_professional": """
<!DOCTYPE html>
<html>
<head><style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
.card {
    width: 700px; height: 400px;
    background: #ffffff;
    border-radius: 12px;
    padding: 48px;
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 8px; height: 100%;
    background: ${accent_color};
}
.top { display: flex; justify-content: space-between; align-items: flex-start; }
.name { font-size: 28px; font-weight: 700; color: #1a1a1a; }
.trade { font-size: 16px; color: #666; margin-top: 4px; font-weight: 400; }
.license { font-size: 12px; color: #999; margin-top: 8px; }
.icon { width: 56px; height: 56px; background: ${accent_color}; border-radius: 12px;
    display: flex; align-items: center; justify-content: center; font-size: 28px; }
.bottom { display: flex; gap: 32px; align-items: center; }
.contact-item { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #444; }
.contact-icon { width: 20px; height: 20px; background: ${accent_color}15; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 11px; }
${watermark_css}
</style></head>
<body>
<div class="card">
    <div class="top">
        <div>
            <div class="name">${business_name}</div>
            <div class="trade">${trade_description}</div>
            <div class="license">${license_text}</div>
        </div>
        <div class="icon">${trade_icon}</div>
    </div>
    <div class="bottom">
        <div class="contact-item">
            <div class="contact-icon">📞</div>
            ${phone}
        </div>
        <div class="contact-item">
            <div class="contact-icon">✉️</div>
            ${email}
        </div>
        <div class="contact-item">
            <div class="contact-icon">📍</div>
            ${location}
        </div>
    </div>
    ${watermark_html}
</div>
</body></html>
""",

    "dark_bold": """
<!DOCTYPE html>
<html>
<head><style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
.card {
    width: 700px; height: 400px;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 12px;
    padding: 48px;
    font-family: 'Montserrat', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.card::after {
    content: '';
    position: absolute;
    top: -50%; right: -20%;
    width: 400px; height: 400px;
    background: ${accent_color}15;
    border-radius: 50%;
}
.name { font-size: 32px; font-weight: 800; color: #ffffff; text-transform: uppercase;
    letter-spacing: 1px; position: relative; z-index: 1; }
.trade { font-size: 15px; color: ${accent_color}; margin-top: 8px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 3px; position: relative; z-index: 1; }
.license { font-size: 12px; color: #ffffff60; margin-top: 12px; position: relative; z-index: 1; }
.divider { width: 60px; height: 3px; background: ${accent_color}; position: relative; z-index: 1; }
.bottom { display: flex; gap: 28px; position: relative; z-index: 1; }
.contact-item { font-size: 14px; color: #ffffffcc; display: flex; align-items: center; gap: 8px; }
.contact-icon { color: ${accent_color}; font-size: 16px; }
${watermark_css}
</style></head>
<body>
<div class="card">
    <div>
        <div class="name">${business_name}</div>
        <div class="trade">${trade_description}</div>
        <div class="license">${license_text}</div>
    </div>
    <div class="divider"></div>
    <div class="bottom">
        <div class="contact-item"><span class="contact-icon">📞</span> ${phone}</div>
        <div class="contact-item"><span class="contact-icon">✉️</span> ${email}</div>
        <div class="contact-item"><span class="contact-icon">📍</span> ${location}</div>
    </div>
    ${watermark_html}
</div>
</body></html>
""",

    "trade_badge": """
<!DOCTYPE html>
<html>
<head><style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700;900&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
.card {
    width: 700px; height: 400px;
    background: #f8f7f4;
    border-radius: 12px;
    padding: 48px;
    font-family: 'Archivo', sans-serif;
    display: flex;
    align-items: center;
    gap: 40px;
    position: relative;
    overflow: hidden;
}
.badge {
    width: 140px; height: 140px;
    background: ${accent_color};
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 8px 32px ${accent_color}40;
}
.badge-icon { font-size: 56px; }
.info { flex: 1; }
.name { font-size: 26px; font-weight: 900; color: #1a1a1a; line-height: 1.1; }
.trade { font-size: 14px; color: ${accent_color}; margin-top: 6px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; }
.license { font-size: 12px; color: #999; margin-top: 8px; padding-top: 8px;
    border-top: 2px solid #eee; }
.contacts { margin-top: 20px; display: flex; flex-direction: column; gap: 6px; }
.contact-item { font-size: 14px; color: #555; }
${watermark_css}
</style></head>
<body>
<div class="card">
    <div class="badge"><span class="badge-icon">${trade_icon}</span></div>
    <div class="info">
        <div class="name">${business_name}</div>
        <div class="trade">${trade_description}</div>
        <div class="license">${license_text}</div>
        <div class="contacts">
            <div class="contact-item">📞 ${phone}</div>
            <div class="contact-item">✉️ ${email}</div>
            <div class="contact-item">📍 ${location}</div>
        </div>
    </div>
    ${watermark_html}
</div>
</body></html>
"""
}

# Watermark overlay for previews
WATERMARK_CSS = """
.watermark {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 48px;
    font-weight: 900;
    color: rgba(0,0,0,0.08);
    letter-spacing: 8px;
    text-transform: uppercase;
    white-space: nowrap;
    z-index: 10;
    pointer-events: none;
}
"""
WATERMARK_HTML = '<div class="watermark">PREVIEW</div>'

# Trade icons mapping
TRADE_ICONS = {
    "plumber": "🔧",
    "plumbing": "🔧",
    "electrician": "⚡",
    "electrical": "⚡",
    "hvac": "❄️",
    "roofing": "🏠",
    "roofer": "🏠",
    "painter": "🎨",
    "painting": "🎨",
    "landscaper": "🌿",
    "landscaping": "🌿",
    "handyman": "🛠️",
    "general contractor": "🏗️",
    "contractor": "🏗️",
    "carpenter": "🪚",
    "carpentry": "🪚",
    "flooring": "🪵",
    "concrete": "🧱",
    "mason": "🧱",
    "welder": "🔥",
    "welding": "🔥",
    "default": "🔨"
}

# Accent colors by trade
TRADE_COLORS = {
    "plumber": "#2563eb",
    "plumbing": "#2563eb",
    "electrician": "#f59e0b",
    "electrical": "#f59e0b",
    "hvac": "#06b6d4",
    "roofing": "#dc2626",
    "roofer": "#dc2626",
    "painter": "#8b5cf6",
    "painting": "#8b5cf6",
    "landscaper": "#16a34a",
    "landscaping": "#16a34a",
    "handyman": "#ea580c",
    "general contractor": "#334155",
    "contractor": "#334155",
    "default": "#2563eb"
}


def get_trade_icon(trade):
    return TRADE_ICONS.get(trade.lower(), TRADE_ICONS["default"])

def get_trade_color(trade):
    return TRADE_COLORS.get(trade.lower(), TRADE_COLORS["default"])


def generate_card_html(card_info, template_name="clean_professional", watermark=True):
    """Generate HTML for a business card design."""
    template = CARD_TEMPLATES.get(template_name, CARD_TEMPLATES["clean_professional"])
    
    trade = card_info.get("trade", "contractor")
    
    # Build substitution dict
    subs = {
        "business_name": card_info.get("business_name", "Your Business Name"),
        "trade_description": card_info.get("trade_description", trade.title()),
        "phone": card_info.get("phone", "(615) 555-0000"),
        "email": card_info.get("email", "info@example.com"),
        "location": card_info.get("location", "Nashville, TN"),
        "license_text": card_info.get("license_text", "Licensed & Insured"),
        "trade_icon": get_trade_icon(trade),
        "accent_color": card_info.get("accent_color", get_trade_color(trade)),
        "watermark_css": WATERMARK_CSS if watermark else "",
        "watermark_html": WATERMARK_HTML if watermark else "",
    }
    
    # Use string.Template for safe substitution
    tmpl = Template(template)
    return tmpl.safe_substitute(subs)


def render_card_to_image(html_content, output_path, width=700, height=400):
    """Render HTML card to PNG using Playwright (headless Chromium)."""
    html_path = output_path.with_suffix('.html')
    png_path = Path(str(output_path).replace('.html', '.png'))
    if png_path.suffix != '.png':
        png_path = output_path.with_suffix('.png')
    
    # Save HTML
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    # Render with Playwright
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width + 100, "height": height + 100})
            page.goto(f"file://{html_path.resolve()}")
            # Wait for Google Fonts to load
            page.wait_for_timeout(1500)
            # Screenshot just the .card element for pixel-perfect output
            card = page.query_selector(".card")
            if card:
                card.screenshot(path=str(png_path))
            else:
                page.screenshot(path=str(png_path), clip={"x": 0, "y": 0, "width": width, "height": height})
            browser.close()
        print(f"✅ Rendered: {png_path}")
        return str(png_path)
    except Exception as e:
        print(f"⚠️  Playwright render failed: {e}")
        print(f"📄 HTML saved: {html_path}")
        print(f"   Install renderer: pip3 install playwright && python3 -m playwright install chromium")
        return str(html_path)


def generate_redesign(card_info, prospect_name, templates=None):
    """Generate full redesign package for a prospect."""
    if templates is None:
        templates = ["clean_professional", "dark_bold", "trade_badge"]
    
    safe_name = prospect_name.lower().replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d")
    results = []
    
    for tmpl_name in templates:
        # Watermarked preview
        html_wm = generate_card_html(card_info, tmpl_name, watermark=True)
        wm_path = WATERMARK_DIR / f"{safe_name}_{tmpl_name}_{timestamp}_preview.png"
        wm_result = render_card_to_image(html_wm, wm_path)
        
        # Clean version (for delivery after payment)
        html_clean = generate_card_html(card_info, tmpl_name, watermark=False)
        clean_path = OUTPUT_DIR / f"{safe_name}_{tmpl_name}_{timestamp}_final.png"
        clean_result = render_card_to_image(html_clean, clean_path)
        
        results.append({
            "template": tmpl_name,
            "preview": wm_result,
            "final": clean_result
        })
    
    print(f"\n✅ Generated {len(results)} redesign variants for {prospect_name}")
    return results


def extract_info_prompt(screenshot_path):
    """Generate the prompt for AI vision extraction of business card info."""
    return f"""Analyze this business card image and extract the following information.
Return it as a JSON object:

{{
    "business_name": "The business or person's name",
    "trade": "Their trade/service (e.g., plumber, electrician)",
    "trade_description": "Full description of services",
    "phone": "Phone number",
    "email": "Email if visible",
    "location": "City/area",
    "license_text": "License number or 'Licensed & Insured'",
    "quality_issues": ["list", "of", "design", "problems"],
    "score": 3
}}

Be specific about quality issues (bad fonts, too many colors, pixelated logo, etc.)
Image: {screenshot_path}"""


# ─── CLI ─────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Business Card Redesign Pipeline")
    subparsers = parser.add_subparsers(dest="command")
    
    # Generate from manual info
    gen = subparsers.add_parser("generate", help="Generate redesign from info")
    gen.add_argument("--name", required=True, help="Business name")
    gen.add_argument("--trade", required=True, help="Trade/service")
    gen.add_argument("--phone", default="(615) 555-0000")
    gen.add_argument("--email", default="")
    gen.add_argument("--location", default="Nashville, TN")
    gen.add_argument("--license", default="Licensed & Insured")
    gen.add_argument("--template", default="all", help="Template name or 'all'")
    gen.add_argument("--prospect", help="Prospect name (for file naming)")
    
    # Extract prompt
    ext = subparsers.add_parser("extract", help="Get AI extraction prompt for a screenshot")
    ext.add_argument("screenshot", help="Path to screenshot")
    
    # List templates
    subparsers.add_parser("templates", help="List available templates")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        card_info = {
            "business_name": args.name,
            "trade": args.trade,
            "trade_description": args.trade.title(),
            "phone": args.phone,
            "email": args.email,
            "location": args.location,
            "license_text": args.license,
        }
        prospect = args.prospect or args.name
        templates = None if args.template == "all" else [args.template]
        generate_redesign(card_info, prospect, templates)
    
    elif args.command == "extract":
        print(extract_info_prompt(args.screenshot))
    
    elif args.command == "templates":
        print("Available templates:")
        for name in CARD_TEMPLATES:
            print(f"  • {name}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
