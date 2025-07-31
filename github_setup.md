# GitHub Setup Commands

After creating your repository on GitHub, run these commands:

```bash
# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/quote-speak-app.git

# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

Example:
```bash
git remote add origin https://github.com/johndoe/quote-speak-app.git
git branch -M main
git push -u origin main
```