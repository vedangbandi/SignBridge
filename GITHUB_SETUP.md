# GitHub Setup Guide

This guide will help you push your Sign Language Recognition System to GitHub.

## Prerequisites

- Git installed on your system ([Download Git](https://git-scm.com/downloads))
- GitHub account ([Sign up](https://github.com/join))

---

## Step 1: Initialize Git Repository

Open your terminal/command prompt in the project directory and run:

```bash
# Navigate to project directory
cd c:\Users\VedangBandiLM\Downloads\Sign-Language-Recognition-System-main

# Initialize git repository
git init

# Check status
git status
```

---

## Step 2: Configure Git (First Time Only)

If you haven't configured Git before:

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email (use your GitHub email)
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

---

## Step 3: Add Files to Git

```bash
# Add all files to staging area
git add .

# Check what will be committed
git status

# You should see files in green (staged for commit)
```

---

## Step 4: Create Initial Commit

```bash
# Create your first commit
git commit -m "Initial commit: Sign Language Recognition System"

# Verify commit
git log
```

---

## Step 5: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click the **"+"** icon in the top-right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `Sign-Language-Recognition-System`
   - **Description**: `Real-time ASL alphabet recognition using deep learning and computer vision`
   - **Visibility**: Choose **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

---

## Step 6: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Sign-Language-Recognition-System.git

# Verify remote
git remote -v

# You should see:
# origin  https://github.com/YOUR_USERNAME/Sign-Language-Recognition-System.git (fetch)
# origin  https://github.com/YOUR_USERNAME/Sign-Language-Recognition-System.git (push)
```

---

## Step 7: Push to GitHub

```bash
# Push to GitHub (first time)
git push -u origin main

# If you get an error about 'main' vs 'master', try:
git branch -M main
git push -u origin main
```

**Note**: You may be prompted to authenticate with GitHub. Use one of these methods:
- **Personal Access Token** (recommended)
- **GitHub CLI** (`gh auth login`)
- **SSH Key**

### Creating a Personal Access Token (if needed):

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **"Generate new token (classic)"**
3. Give it a name: `Sign Language Recognition System`
4. Select scopes: Check **"repo"** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

---

## Step 8: Verify Upload

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/Sign-Language-Recognition-System`
2. You should see all your files
3. The README.md will be displayed on the main page

---

## Important Notes

### Large Files Warning

⚠️ **GitHub has a 100MB file size limit and 1GB repository size limit.**

Your project contains:
- `MP_Data/` directory with 22,500 files (~500MB+)
- `model.h5` file (~2.3MB)

**Options:**

#### Option 1: Include Everything (if under 1GB)
```bash
# Already done in Step 3
git add .
git commit -m "Initial commit with dataset"
git push
```

#### Option 2: Exclude Large Dataset
If the dataset is too large, exclude it:

1. Edit `.gitignore` and uncomment:
   ```
   MP_Data/
   ```

2. Remove from git if already added:
   ```bash
   git rm -r --cached MP_Data
   git commit -m "Remove large dataset from repository"
   ```

3. Add a note in README about downloading the dataset separately

#### Option 3: Use Git LFS (Large File Storage)
For files over 100MB:

```bash
# Install Git LFS
# Windows: Download from https://git-lfs.github.com/
# Linux: sudo apt-get install git-lfs
# macOS: brew install git-lfs

# Initialize Git LFS
git lfs install

# Track large files
git lfs track "*.h5"
git lfs track "MP_Data/**/*.npy"

# Add .gitattributes
git add .gitattributes

# Commit and push
git commit -m "Add Git LFS tracking"
git push
```

---

## Future Updates

After making changes to your code:

```bash
# Check what changed
git status

# Add changed files
git add .

# Or add specific files
git add filename.py

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

---

## Common Git Commands

```bash
# View commit history
git log

# View short commit history
git log --oneline

# View changes before committing
git diff

# Undo changes to a file (before staging)
git checkout -- filename.py

# Unstage a file
git reset HEAD filename.py

# View remote repositories
git remote -v

# Pull latest changes from GitHub
git pull

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch into main
git checkout main
git merge feature-name
```

---

## Customizing Your README

Before pushing, update these sections in `README.md`:

1. **Line 10**: Replace `[Your Name](https://github.com/yourusername)` with your actual name and GitHub username
2. **Line 75**: Update the repository URL
3. **Line 85**: Update clone URL with your username
4. **Line 400**: Update contact email
5. **Line 420**: Update citation with your name

**Quick find and replace:**
```bash
# In README.md, replace:
yourusername → YOUR_GITHUB_USERNAME
your.email@example.com → YOUR_EMAIL
Your Name → YOUR_ACTUAL_NAME
```

---

## Adding a Repository Description

On GitHub:
1. Go to your repository
2. Click the ⚙️ (Settings) icon next to "About"
3. Add description: `Real-time ASL alphabet recognition using deep learning and computer vision`
4. Add topics: `machine-learning`, `deep-learning`, `computer-vision`, `sign-language`, `tensorflow`, `opencv`, `mediapipe`, `lstm`, `python`
5. Add website (if you have one)
6. Click **"Save changes"**

---

## Adding a License Badge

Your README already includes a GPL-3.0 license badge. Make sure your `LICENSE` file matches.

---

## Troubleshooting

### Issue: "Permission denied (publickey)"
**Solution**: Set up SSH key or use HTTPS with Personal Access Token

### Issue: "Repository not found"
**Solution**: Check the remote URL is correct:
```bash
git remote -v
git remote set-url origin https://github.com/YOUR_USERNAME/Sign-Language-Recognition-System.git
```

### Issue: "Failed to push some refs"
**Solution**: Pull first, then push:
```bash
git pull origin main --rebase
git push origin main
```

### Issue: "File too large"
**Solution**: Use Git LFS or exclude the file in `.gitignore`

---

## Next Steps

After pushing to GitHub:

1. ✅ Add repository description and topics
2. ✅ Enable GitHub Pages (if you want a website)
3. ✅ Add collaborators (Settings → Collaborators)
4. ✅ Set up branch protection rules
5. ✅ Create issues for future features
6. ✅ Add a CONTRIBUTING.md guide
7. ✅ Star your own repository! ⭐

---

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git LFS](https://git-lfs.github.com/)
- [Markdown Guide](https://www.markdownguide.org/)

---

**Good luck with your GitHub repository! 🚀**
