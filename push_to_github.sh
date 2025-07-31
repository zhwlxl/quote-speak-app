#!/bin/bash

echo "🚀 Pushing to GitHub..."

# Check if user provided username
if [ -z "$1" ]; then
    echo "❌ Please provide your GitHub username"
    echo "Usage: ./push_to_github.sh YOUR_GITHUB_USERNAME"
    echo "Example: ./push_to_github.sh johndoe"
    exit 1
fi

USERNAME=$1
REPO_URL="https://github.com/$USERNAME/quote-speak-app.git"

echo "📝 Repository URL: $REPO_URL"

# Add remote
echo "Adding remote origin..."
git remote add origin $REPO_URL

# Rename branch to main
echo "Renaming branch to main..."
git branch -M main

# Push to GitHub
echo "Pushing to GitHub..."
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 Your repository: https://github.com/$USERNAME/quote-speak-app"
echo ""
echo "Next step: Go to render.com and deploy!"