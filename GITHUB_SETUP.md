# GitHub Repository Setup

Your local repository is ready! Follow these steps to push to GitHub:

## Quick Setup (Choose One Method)

### Method 1: Interactive Script (Recommended)
```bash
./setup_github.sh
```
This script will guide you through the process.

### Method 2: Manual Commands

1. **Create repository on GitHub:**
   - Visit: https://github.com/new
   - Name: `android-forensics-tool` (or your choice)
   - Choose Public/Private
   - **DO NOT** initialize with README, .gitignore, or license
   - Click "Create repository"

2. **Run these commands:**
```bash
# Set your repository name (change if different)
REPO_NAME="android-forensics-tool"
GITHUB_USER="youssefbayoumy"

# Add remote
git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git

# Push to GitHub
git push -u origin main
```

## Authentication

If prompted for credentials:
- **Username**: your GitHub username
- **Password**: Use a Personal Access Token (not your GitHub password)
  - Create token: https://github.com/settings/tokens
  - Select `repo` scope
  - Copy and use as password

## Current Status

✅ Git repository initialized  
✅ All files committed  
✅ Branch set to `main`  
⏳ Waiting for GitHub repository creation and push

