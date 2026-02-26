#!/bin/bash
# Quick script to verify Xiaomi Mimo configuration

echo "🔍 Checking HiveTerminal configuration for Xiaomi Mimo..."
echo ""

CONFIG_FILE="$HOME/.vibe/config.toml"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found at $CONFIG_FILE"
    echo "   Run 'hive --setup' to create it"
    exit 1
fi

echo "1. Checking active_model..."
ACTIVE_MODEL=$(grep "^active_model" "$CONFIG_FILE" | cut -d'"' -f2)
if [ "$ACTIVE_MODEL" = "xiaomi_mimo/mimo-v2-flash" ]; then
    echo "   ✅ Active model is set to: $ACTIVE_MODEL"
else
    echo "   ⚠️  Active model is: $ACTIVE_MODEL"
    echo "      Expected: xiaomi_mimo/mimo-v2-flash"
fi
echo ""

echo "2. Checking xiaomi_mimo provider..."
if grep -q 'name = "xiaomi_mimo"' "$CONFIG_FILE"; then
    echo "   ✅ xiaomi_mimo provider found"
    PROVIDER_BACKEND=$(grep -A 5 'name = "xiaomi_mimo"' "$CONFIG_FILE" | grep "backend" | cut -d'"' -f2)
    echo "      Backend: $PROVIDER_BACKEND"
else
    echo "   ❌ xiaomi_mimo provider NOT found"
    echo "      Run the fix script from XIAOMI_MODEL_SELECTION_FIX.md"
fi
echo ""

echo "3. Checking mimo-v2-flash model..."
if grep -q 'name = "mimo-v2-flash"' "$CONFIG_FILE"; then
    echo "   ✅ mimo-v2-flash model found"
    MODEL_PROVIDER=$(grep -B 1 'name = "mimo-v2-flash"' "$CONFIG_FILE" | grep "provider" | cut -d'"' -f2)
    MODEL_ALIAS=$(grep -A 1 'name = "mimo-v2-flash"' "$CONFIG_FILE" | grep "alias" | cut -d'"' -f2)
    echo "      Provider: $MODEL_PROVIDER"
    echo "      Alias: $MODEL_ALIAS"
else
    echo "   ❌ mimo-v2-flash model NOT found"
    echo "      Run the fix script from XIAOMI_MODEL_SELECTION_FIX.md"
fi
echo ""

echo "4. Checking API key..."
ENV_FILE="$HOME/.vibe/.env"
if [ -f "$ENV_FILE" ] && grep -q "XIAOMI_MIMO_API_KEY" "$ENV_FILE"; then
    echo "   ✅ XIAOMI_MIMO_API_KEY found in $ENV_FILE"
elif [ -n "$XIAOMI_MIMO_API_KEY" ]; then
    echo "   ✅ XIAOMI_MIMO_API_KEY found in environment"
else
    echo "   ⚠️  XIAOMI_MIMO_API_KEY not found"
    echo "      Set it in $ENV_FILE or export it"
    echo "      Get your key from: https://platform.xiaomimimo.com/#/console/api-keys"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$ACTIVE_MODEL" = "xiaomi_mimo/mimo-v2-flash" ] && \
   grep -q 'name = "xiaomi_mimo"' "$CONFIG_FILE" && \
   grep -q 'name = "mimo-v2-flash"' "$CONFIG_FILE"; then
    echo "✅ Configuration looks good! You can run 'hive' now."
else
    echo "⚠️  Configuration needs fixing. See XIAOMI_MODEL_SELECTION_FIX.md"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
