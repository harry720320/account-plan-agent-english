# GitHub Push Troubleshooting Guide

## Error: "push declined due to repository rule violations"

This error occurs when the GitHub repository has branch protection rules enabled.

## Quick Solutions

### Solution 1: Disable Branch Protection (Recommended for new repos)

1. Go to your GitHub repository
2. Click **Settings** → **Branches**
3. Under "Branch protection rules", if there's a rule for `main`:
   - Click **Edit** or **Delete**
   - Temporarily disable or delete the rule
4. Try pushing again:
   ```cmd
   git_push.bat
   ```

### Solution 2: Push to a Different Branch First

```cmd
# Push to a different branch
git push -u origin main:initial-release

# Then create a Pull Request on GitHub
# After merging, the code will be on main branch
```

### Solution 3: Force Push (Use with caution!)

⚠️ **Only use this for a brand new repository with no important data**

```cmd
git push -u origin main --force
```

### Solution 4: Use Personal Access Token with Admin Rights

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes:
   - ✅ repo (Full control)
   - ✅ workflow
   - ✅ admin:repo_hook
4. Copy the token
5. When pushing, use the token as password

## Detailed Steps for Solution 1 (Recommended)

### Step 1: Check Branch Protection Rules

1. Go to: `https://github.com/harry720320/account-plan-agent-english/settings/branches`
2. Look for "Branch protection rules"
3. If you see a rule for `main` or `*` (all branches), that's the issue

### Step 2: Modify or Remove Protection

**Option A: Temporarily Disable**
- Click **Edit** on the protection rule
- Uncheck all requirements
- Click **Save changes**
- Push your code
- Re-enable protections after initial push

**Option B: Delete the Rule**
- Click **Delete** on the protection rule
- Confirm deletion
- Push your code
- Add protections back later if needed

### Step 3: Push Again

```cmd
git_push.bat
```

## Common Protection Rules That Block Pushes

1. **Require pull request reviews** - Can't push directly
2. **Require status checks** - Need CI/CD to pass first
3. **Require signed commits** - Need GPG signing
4. **Restrict who can push** - Your account not in allowed list
5. **Require linear history** - Can't force push

## Alternative: Initial Release Without Branch Protection

For brand new repositories, it's common to:

1. Push initial code **without** branch protection
2. Set up branch protection **after** code is there
3. Use pull requests for future changes

## Quick Check Script

Run this to see current remote settings:

```cmd
git remote -v
git branch -a
git log --oneline -5
```

## If Still Having Issues

### Check Repository Settings

1. **Repository visibility**: Make sure it's set correctly (Public/Private)
2. **Repository permissions**: Ensure you have write access
3. **Organization rules**: If in an organization, check org-level rules

### Try GitHub CLI

```cmd
# Install GitHub CLI if not already installed
# Then authenticate and push
gh auth login
gh repo view harry720320/account-plan-agent-english
git push -u origin main
```

## For Existing Repository with Code

If the repository already has code and you're replacing it:

```cmd
# Fetch existing code
git fetch origin

# Merge or rebase
git merge origin/main --allow-unrelated-histories

# Then push
git push -u origin main
```

## Best Practice for New Repositories

**Recommended Initial Setup:**

1. Create empty repository on GitHub (no README, no .gitignore)
2. Push your code first without any protections
3. After successful initial push, set up:
   - Branch protection rules
   - Required reviewers
   - Status checks
   - Any other rules you need

## Contact Information

If none of these solutions work:
- Check GitHub Status: https://www.githubstatus.com/
- GitHub Support: https://support.github.com/

---

**Most Common Fix**: Go to Settings → Branches → Remove or modify protection rule → Try pushing again

