#!/bin/bash

# Script to connect local repository to GitHub and push

REPO_NAME="android-forensics-tool"
GITHUB_USER="youssefbayoumy"

echo "=== GitHub Repository Setup ==="
echo ""
echo "This script will help you push your code to GitHub."
echo ""
echo "Step 1: Create a new repository on GitHub"
echo "  1. Go to: https://github.com/new"
echo "  2. Repository name: $REPO_NAME (or choose your own)"
echo "  3. Set it to Public or Private"
echo "  4. DO NOT initialize with README, .gitignore, or license"
echo "  5. Click 'Create repository'"
echo ""
read -p "Have you created the repository? (y/n): " created

if [ "$created" != "y" ] && [ "$created" != "Y" ]; then
    echo "Please create the repository first, then run this script again."
    exit 1
fi

echo ""
read -p "Enter your GitHub repository name [default: $REPO_NAME]: " custom_name
if [ ! -z "$custom_name" ]; then
    REPO_NAME="$custom_name"
fi

echo ""
echo "Step 2: Adding remote and pushing..."
echo ""

# Add remote
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Remote might already exist. Updating..."
    git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
fi

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Successfully pushed to GitHub!"
    echo "Repository URL: https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo ""
    echo "✗ Push failed. You may need to:"
    echo "  1. Authenticate with GitHub (git credential helper)"
    echo "  2. Use a personal access token as password"
    echo "  3. Or set up SSH keys"
    echo ""
    echo "To use a personal access token:"
    echo "  - Go to: https://github.com/settings/tokens"
    echo "  - Generate a new token with 'repo' permissions"
    echo "  - Use the token as your password when prompted"
fi

