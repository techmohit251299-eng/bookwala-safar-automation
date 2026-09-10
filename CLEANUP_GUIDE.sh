#!/bin/bash

# 🗑️ Cleanup Script - Unused Files Remove Karna

echo "Removing old script files..."

# Remove old versions (KEPT FOR REFERENCE, remove if needed)
# git rm scripts/generate_script_anthropic.py
# git rm scripts/generate_script_enhanced.py

# If you want to keep them, you can also just delete from repo manually
# This is a reminder of which files are safe to remove

echo "Files to keep:"
echo "✅ scripts/generate_script_enhanced_v2.py (PRODUCTION)"
echo "✅ scripts/generate_voice.py"
echo "✅ scripts/select_book.py"

echo ""
echo "Files to remove (optional):"
echo "❌ scripts/generate_script_anthropic.py (OLD - basic version)"
echo "❌ scripts/generate_script_enhanced.py (OLD - fake pronunciation fix)"
echo "❌ CODE_REVIEW_FIXES.md (reference only)"
