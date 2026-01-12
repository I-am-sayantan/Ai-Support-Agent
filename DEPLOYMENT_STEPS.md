# 🚀 Deployment Checklist

## ✅ What's Already Done:

- ✅ Azure Web App created: `ai-support-agent`
- ✅ Resource Group: `ai-support-agent`
- ✅ App Service Plan: B1 (Basic tier)
- ✅ GitHub Actions workflow configured
- ✅ Docker configuration ready

---

## 📋 What You Need to Do Now:

### Step 1: Download Publish Profile from Azure Portal

1. **In Azure Portal** (the page you have open):
   - Click the **"Get publish profile"** or **"Download publish profile"** button at the top
   - Save the file `ai-support-agent.PublishSettings`
2. **Open the file in Notepad**
   - Copy ALL the content (it's XML format)

### Step 2: Create/Update GitHub Repository

**If you haven't pushed to GitHub yet:**

```powershell
# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment setup"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

### Step 3: Add GitHub Secrets

Go to: `https://github.com/YOUR-USERNAME/YOUR-REPO/settings/secrets/actions`

Click **"New repository secret"** and add these **5 secrets**:

| Secret Name                         | Value                                                                                  |
| ----------------------------------- | -------------------------------------------------------------------------------------- |
| `AZURE_WEBAPP_PUBLISH_PROFILE`      | Paste entire XML from Step 1                                                           |
| `AZURE_OPENAI_API_KEY`              | `BbnhzAFttbZCwUbTmQwYYFtCN8iuagBws4UOmEk1sl4fnXc29T1JJQQJ99CAACHYHv6XJ3w3AAAAACOGmqO5` |
| `AZURE_OPENAI_ENDPOINT`             | `https://sayan-mka1tkzo-eastus2.cognitiveservices.azure.com/`                          |
| `AZURE_OPENAI_DEPLOYMENT`           | `sayantan-chat`                                                                        |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | `sayantan-embed`                                                                       |

### Step 4: Push to GitHub and Deploy

```powershell
# After adding secrets, just push:
git add .
git commit -m "Deploy to Azure"
git push origin main
```

**GitHub Actions will automatically:**

- Build your Docker image
- Push to GitHub Container Registry
- Deploy to Azure App Service
- Configure environment variables
- Your app will be live!

### Step 5: Monitor Deployment

1. **Go to GitHub Actions tab**: `https://github.com/YOUR-USERNAME/YOUR-REPO/actions`
2. **Watch the workflow** run (takes about 5-10 minutes)
3. **When complete**, your app will be at: `https://ai-support-agent.azurewebsites.net`

---

## 🌐 Your App URLs (after deployment):

- **Main URL**: https://ai-support-agent.azurewebsites.net
- **API Docs**: https://ai-support-agent.azurewebsites.net/docs
- **Health Check**: https://ai-support-agent.azurewebsites.net/health

---

## 🔄 Future Updates:

Just commit and push to main branch:

```powershell
git add .
git commit -m "Updated feature"
git push origin main
# GitHub Actions will automatically redeploy!
```

---

## ⚠️ Important Notes:

1. **Make your GitHub repo public** OR **keep it private** (both work with GitHub Container Registry)
2. **Container Registry**: Using GitHub Container Registry (ghcr.io) - it's free!
3. **No Azure CLI needed** - Everything works via GitHub Actions
4. **Cost**: Azure B1 plan costs ~$13/month + Azure OpenAI usage

---

## 🐛 Troubleshooting:

### If deployment fails:

1. Check GitHub Actions logs
2. Verify all 5 secrets are added correctly
3. Make sure publish profile is the complete XML

### If app doesn't start:

1. In Azure Portal, go to your web app
2. Click "Log stream" to see real-time logs
3. Check environment variables are set correctly

---

## ✨ That's It!

Once you complete these steps, your AI Support Agent will be live on Azure! 🎉
