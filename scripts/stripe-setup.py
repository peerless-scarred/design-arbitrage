#!/usr/bin/env python3
"""
Stripe Product & Webhook Setup for Design Arbitrage
=====================================================
Creates Stripe products, payment links, and handles webhook delivery.

Products:
  - Business Card Redesign ($50) — 3 design options, print-ready files
  - Rush Redesign ($75) — Same day delivery
  - Card + Logo Package ($150) — Full brand refresh

Setup:
  1. pip install stripe
  2. Set STRIPE_SECRET_KEY environment variable
  3. Run: python stripe-setup.py create-products
  4. Run: python stripe-setup.py webhook-server (for delivery automation)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
STRIPE_CONFIG = PROJECT_ROOT / "config" / "stripe.json"


def get_stripe():
    """Import and configure stripe."""
    try:
        import stripe
    except ImportError:
        print("❌ Install stripe: pip install stripe")
        sys.exit(1)
    
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe.api_key:
        print("❌ Set STRIPE_SECRET_KEY environment variable")
        print("   Get your key at: https://dashboard.stripe.com/apikeys")
        sys.exit(1)
    
    return stripe


def create_products():
    """Create Stripe products and prices."""
    stripe = get_stripe()
    
    products_config = [
        {
            "name": "Business Card Redesign",
            "description": "Professional business card redesign — 3 design options, print-ready PDF & PNG files, unlimited revisions",
            "price": 5000,  # $50.00 in cents
            "metadata": {
                "type": "card_redesign",
                "delivery": "24h",
                "includes": "3 designs, print-ready files, revision"
            }
        },
        {
            "name": "Rush Business Card Redesign",
            "description": "Same-day professional redesign — 3 options delivered within 4 hours",
            "price": 7500,  # $75.00
            "metadata": {
                "type": "rush_redesign",
                "delivery": "4h",
                "includes": "3 designs, print-ready files, priority"
            }
        },
        {
            "name": "Business Card + Logo Package",
            "description": "Complete brand refresh — new logo design + business card + social media profile graphics",
            "price": 15000,  # $150.00
            "metadata": {
                "type": "full_package",
                "delivery": "48h",
                "includes": "logo, card, social graphics, brand guide"
            }
        }
    ]
    
    created = []
    for p in products_config:
        print(f"\n📦 Creating: {p['name']}...")
        
        product = stripe.Product.create(
            name=p["name"],
            description=p["description"],
            metadata=p["metadata"]
        )
        
        price = stripe.Price.create(
            product=product.id,
            unit_amount=p["price"],
            currency="usd"
        )
        
        # Create payment link
        payment_link = stripe.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}],
            after_completion={
                "type": "redirect",
                "redirect": {"url": "https://yourdomain.com/thank-you?session_id={CHECKOUT_SESSION_ID}"}
            },
            metadata=p["metadata"]
        )
        
        result = {
            "product_id": product.id,
            "price_id": price.id,
            "payment_link_id": payment_link.id,
            "payment_url": payment_link.url,
            "amount": p["price"] / 100,
            "name": p["name"]
        }
        created.append(result)
        
        print(f"  ✅ Product: {product.id}")
        print(f"  💰 Price: ${p['price']/100:.2f}")
        print(f"  🔗 Payment link: {payment_link.url}")
    
    # Save config
    STRIPE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    with open(STRIPE_CONFIG, 'w') as f:
        json.dump({"products": created, "created": datetime.now().isoformat()}, f, indent=2)
    
    print(f"\n✅ All products created! Config saved to: {STRIPE_CONFIG}")
    return created


def create_webhook_server():
    """Generate a simple webhook server for payment notifications."""
    
    server_code = '''#!/usr/bin/env python3
"""
Stripe Webhook Server — Handles payment completion and file delivery.
Run: python webhook-server.py
Expose: ngrok http 4242 (for testing)
"""
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path
from flask import Flask, request, jsonify
import stripe

app = Flask(__name__)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
REDESIGNS_DIR = Path(__file__).parent.parent / "assets" / "redesigns"

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError:
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_details", {}).get("email")
        customer_name = session.get("customer_details", {}).get("name", "Customer")
        metadata = session.get("metadata", {})
        
        print(f"💰 Payment received from {customer_email}")
        print(f"   Type: {metadata.get('type', 'unknown')}")
        
        # Trigger file delivery
        deliver_files(customer_email, customer_name, metadata)
    
    return jsonify({"status": "ok"}), 200


def deliver_files(email, name, metadata):
    """Deliver redesign files to customer via email."""
    prospect_name = metadata.get("prospect_name", "customer")
    safe_name = prospect_name.lower().replace(" ", "_")
    
    # Find their files
    files = list(REDESIGNS_DIR.glob(f"{safe_name}_*_final.*"))
    
    if not files:
        print(f"⚠️ No files found for {prospect_name} — manual delivery needed")
        return
    
    # Send via email (configure SMTP settings)
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    
    if not smtp_user:
        print(f"📧 Email delivery not configured. Files ready at: {REDESIGNS_DIR}")
        for f in files:
            print(f"   → {f}")
        return
    
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = email
    msg["Subject"] = f"Your Professional Business Card Redesign — {name}"
    
    body = f"""Hi {name},

Thank you for your order! Your professional business card redesigns are attached.

What's included:
• 3 unique design variations
• Print-ready PNG files (300 DPI)
• Files sized for standard 3.5" × 2" business cards

NEXT STEPS:
1. Pick your favorite design
2. Reply to this email if you want any changes (unlimited revisions!)
3. Ready to print? I recommend Vistaprint or MOO for premium quality

Need any changes? Just reply to this email and I'll take care of it.

Best,
[Your Name]
Design Arbitrage Co.
"""
    msg.attach(MIMEText(body, "plain"))
    
    for filepath in files:
        with open(filepath, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filepath.name}")
            msg.attach(part)
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, email, msg.as_string())
        print(f"✅ Files delivered to {email}")
    except Exception as e:
        print(f"❌ Email failed: {e}")
        print(f"   Files ready for manual delivery at: {REDESIGNS_DIR}")


if __name__ == "__main__":
    print("🚀 Webhook server running on port 4242")
    print("   Expose with: ngrok http 4242")
    app.run(port=4242)
'''
    
    server_path = PROJECT_ROOT / "scripts" / "webhook-server.py"
    with open(server_path, 'w') as f:
        f.write(server_code)
    
    print(f"✅ Webhook server created: {server_path}")
    print("\nTo run:")
    print("  1. pip install flask stripe")
    print("  2. export STRIPE_SECRET_KEY=sk_...")
    print("  3. export STRIPE_WEBHOOK_SECRET=whsec_...")
    print("  4. python webhook-server.py")
    print("  5. ngrok http 4242 (for testing)")


def load_stripe_config():
    """Load saved Stripe config."""
    if STRIPE_CONFIG.exists():
        with open(STRIPE_CONFIG) as f:
            return json.load(f)
    return None


def show_payment_links():
    """Display all payment links."""
    config = load_stripe_config()
    if not config:
        print("❌ No Stripe config found. Run: python stripe-setup.py create-products")
        return
    
    print("\n🔗 PAYMENT LINKS")
    print("=" * 60)
    for p in config["products"]:
        print(f"\n  {p['name']} — ${p['amount']:.2f}")
        print(f"  {p['payment_url']}")
    print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stripe Setup for Design Arbitrage")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("create-products", help="Create Stripe products")
    subparsers.add_parser("create-webhook", help="Generate webhook server")
    subparsers.add_parser("links", help="Show payment links")
    
    args = parser.parse_args()
    
    if args.command == "create-products":
        create_products()
    elif args.command == "create-webhook":
        create_webhook_server()
    elif args.command == "links":
        show_payment_links()
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("  1. python stripe-setup.py create-products")
        print("  2. python stripe-setup.py create-webhook")


if __name__ == "__main__":
    main()
