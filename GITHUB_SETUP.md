# GitHub Setup Instructions

After pushing to GitHub, update these files with your actual GitHub username/repository:

## Files to Update

### 1. install.sh
Replace `Tushar04-Master` with your GitHub username:
```bash
# Line 4:
# Usage: curl -fsSL https://raw.githubusercontent.com/Tushar04-Master/HiveTerminal/main/install.sh | bash

# Line 73:
git clone https://github.com/Tushar04-Master/HiveTerminal.git "$INSTALL_DIR"
```

### 2. README.md
Replace `Tushar04-Master` with your GitHub username:
```bash
# In the "One-Line Installation" section:
curl -fsSL https://raw.githubusercontent.com/Tushar04-Master/HiveTerminal/main/install.sh | bash
```

### 3. INSTALL.md
Replace `Tushar04-Master` with your GitHub username:
```bash
# Multiple locations - search and replace all instances
```

## Quick Find & Replace

Run this command in your repository root (replace `yourusername` with your actual GitHub username):

```bash
# macOS:
find . -type f \( -name "*.sh" -o -name "*.md" \) -exec sed -i '' 's/Tushar04-Master/yourusername/g' {} +

# Linux:
find . -type f \( -name "*.sh" -o -name "*.md" \) -exec sed -i 's/Tushar04-Master/yourusername/g' {} +
```

## After Updating

1. Commit the changes:
```bash
git add install.sh README.md INSTALL.md
git commit -m "Update GitHub URLs with actual username"
git push origin main
```

2. Test the one-line installer:
```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/hiveterminal/master/install.sh | bash
```

## Making install.sh Accessible

The one-line installer works by fetching the script from GitHub's raw content URL. Make sure:

1. ✅ Repository is public (or use a personal access token for private repos)
2. ✅ `install.sh` is in the repository root
3. ✅ File is committed and pushed to the `main` branch
4. ✅ URLs are updated with your actual username

## Testing the Installer

Before sharing with others, test it:

```bash
# Test in a clean environment (Docker or VM recommended)
curl -fsSL https://raw.githubusercontent.com/yourusername/hiveterminal/master/install.sh | bash

# Or download and inspect first:
curl -fsSL https://raw.githubusercontent.com/yourusername/hiveterminal/master/install.sh > test-install.sh
cat test-install.sh  # Review the script
bash test-install.sh
```

## Sharing the Installation Command

Once everything is set up, users can install with:

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/hiveterminal/master/install.sh | bash
```

Add this to your README's Quick Start section!
