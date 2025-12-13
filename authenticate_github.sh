#!/bin/bash

echo "=== GitHub Authentication Setup ==="
echo ""
echo "To push to GitHub, you need to authenticate using a Personal Access Token."
echo ""
echo "Step 1: Create a Personal Access Token"
echo "  1. Go to: https://github.com/settings/tokens"
echo "  2. Click 'Generate new token' → 'Generate new token (classic)'"
echo "  3. Give it a name (e.g., 'AndroidForensicsTool')"
echo "  4. Select expiration (30 days, 90 days, or no expiration)"
echo "  5. Check the 'repo' scope (full control of private repositories)"
echo "  6. Click 'Generate token'"
echo "  7. COPY THE TOKEN IMMEDIATELY (you won't see it again!)"
echo ""
read -p "Have you created and copied your token? (y/n): " token_ready

if [ "$token_ready" != "y" ] && [ "$token_ready" != "Y" ]; then
    echo "Please create the token first, then run this script again."
    exit 1
fi

echo ""
echo "Step 2: Pushing to GitHub"
echo "When prompted:"
echo "  Username: youssefbayoumy"
echo "  Password: [paste your personal access token]"
echo ""
read -p "Press Enter to continue with push..."

cd "$(dirname "$0")"
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Successfully pushed to GitHub!"
    echo "Repository: https://github.com/youssefbayoumy/AndroidForensicsTool"
else
    echo ""
    echo "✗ Push failed. Please check:"
    echo "  1. Your token has 'repo' permissions"
    echo "  2. You copied the token correctly"
    echo "  3. The repository exists at: https://github.com/youssefbayoumy/AndroidForensicsTool"
fi

