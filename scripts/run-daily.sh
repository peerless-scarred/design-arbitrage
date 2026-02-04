#!/bin/bash
# ============================================================
# Daily Design Arbitrage Workflow
# Run this each morning to execute the full pipeline
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo "🎨 DESIGN ARBITRAGE — Daily Run"
echo "   $(date '+%A, %B %d, %Y at %I:%M %p')"
echo "=================================================="

# Step 1: Open monitoring groups
echo ""
echo "📋 STEP 1: Monitor Facebook Groups"
echo "-----------------------------------"
python3 "$SCRIPT_DIR/fb-group-monitor.py" monitor --tier 1

echo ""
echo "⏸️  Browse the groups above. When you find a bad business card:"
echo "   1. Screenshot it (Cmd+Shift+4)"
echo "   2. Save to: $PROJECT_DIR/assets/screenshots/"
echo ""
read -p "Press Enter when done browsing (or 'skip' to skip)... " response

if [ "$response" != "skip" ]; then
    # Step 2: Add prospects
    echo ""
    echo "📝 STEP 2: Add New Prospects"
    echo "-----------------------------------"
    while true; do
        read -p "Add a prospect? (y/n): " add
        [ "$add" != "y" ] && break
        
        read -p "  Business name: " biz_name
        read -p "  Trade: " trade
        read -p "  Phone: " phone
        read -p "  Source group: " group
        read -p "  Card score (1-10): " score
        read -p "  Notes: " notes
        
        python3 "$SCRIPT_DIR/fb-group-monitor.py" add \
            "$biz_name" "$trade" \
            --phone "$phone" \
            --group "$group" \
            --score "$score" \
            --notes "$notes"
        
        # Auto-generate redesign
        echo ""
        echo "🎨 Generating redesigns..."
        safe_name=$(echo "$biz_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd 'a-z0-9_')
        python3 "$SCRIPT_DIR/redesign-pipeline.py" generate \
            --name "$biz_name" \
            --trade "$trade" \
            --phone "$phone" \
            --location "Tennessee" \
            --prospect "$safe_name"
        
        echo ""
        echo "📤 Preview files ready in: $PROJECT_DIR/assets/watermarked/"
        echo "   Open the HTML files in your browser to see designs."
    done
fi

# Step 3: Daily report
echo ""
echo "📊 STEP 3: Daily Report"
echo "-----------------------------------"
python3 "$SCRIPT_DIR/fb-group-monitor.py" report

# Step 4: Pending contacts
echo ""
echo "📨 STEP 4: Prospects Ready to Contact"
echo "-----------------------------------"
python3 "$SCRIPT_DIR/fb-group-monitor.py" list --status new

echo ""
echo "💡 To send a DM:"
echo "   1. Open the watermarked preview for the prospect"
echo "   2. Copy Template A from: templates/dm-messages.md"
echo "   3. Fill in the variables and send via Facebook Messenger"
echo "   4. Update status: python3 fb-group-monitor.py update <ID> contacted"
echo ""
echo "=================================================="
echo "✅ Daily run complete!"
echo "=================================================="
