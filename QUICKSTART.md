# Quick Start - Docker & Azure Deployment

## Local Testing with Docker

### 1. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_DEPLOYMENT
# - AZURE_OPENAI_EMBEDDING_DEPLOYMENT
```

### 2. Build and Run with Docker

**Option A: Using Docker Compose (Recommended)**

```bash
docker-compose up --build
```

**Option B: Using Docker directly**

```bash
# Build image
docker build -t ai-support-agent:latest .

# Run container
docker run -p 8000:8000 \
  -e AZURE_OPENAI_API_KEY=your-key \
  -e AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/ \
  -e AZURE_OPENAI_DEPLOYMENT=gpt-4 \
  -e AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002 \
  -v $(pwd)/documents:/app/documents:ro \
  -v $(pwd)/rag_index:/app/rag_index \
  ai-support-agent:latest
```

### 3. Test the Application

```bash
# Health check
curl http://localhost:8000/health

# Interactive API docs
open http://localhost:8000/docs

# Test query
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the company policies?"}'
```

## Azure Deployment

### Quick Deploy (PowerShell - Windows)

```powershell
# Edit the script to set your configuration
.\deploy-azure.ps1 `
  -ResourceGroup "my-resource-group" `
  -AppName "my-ai-agent" `
  -ACRName "myregistry" `
  -Location "eastus"
```

### Quick Deploy (Bash - Linux/Mac)

```bash
# Edit the script to set your configuration
chmod +x deploy-azure.sh
./deploy-azure.sh
```

### Manual Deployment Steps

1. **Build and push to Azure Container Registry**

   ```bash
   # Login to ACR
   az acr login --name yourregistry

   # Build and push
   docker build -t yourregistry.azurecr.io/ai-support-agent:latest .
   docker push yourregistry.azurecr.io/ai-support-agent:latest
   ```

2. **Create Web App**

   ```bash
   az webapp create \
     --resource-group your-rg \
     --plan your-plan \
     --name your-app-name \
     --deployment-container-image-name yourregistry.azurecr.io/ai-support-agent:latest
   ```

3. **Configure Environment Variables**

   ```bash
   az webapp config appsettings set \
     --resource-group your-rg \
     --name your-app-name \
     --settings \
       AZURE_OPENAI_API_KEY="your-key" \
       AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
       AZURE_OPENAI_DEPLOYMENT="gpt-4" \
       AZURE_OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-ada-002" \
       WEBSITES_PORT=8000
   ```

4. **Access Your Application**
   - URL: `https://your-app-name.azurewebsites.net`
   - Docs: `https://your-app-name.azurewebsites.net/docs`

## Environment Variables

| Variable                                | Description                               | Required |
| --------------------------------------- | ----------------------------------------- | -------- |
| `AZURE_OPENAI_API_KEY`                  | Azure OpenAI API key                      | Yes      |
| `AZURE_OPENAI_ENDPOINT`                 | Azure OpenAI endpoint URL                 | Yes      |
| `AZURE_OPENAI_DEPLOYMENT`               | GPT model deployment name                 | Yes      |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`     | Embedding model deployment name           | Yes      |
| `AZURE_OPENAI_API_VERSION`              | API version (default: 2024-12-01-preview) | No       |
| `PORT`                                  | Server port (default: 8000)               | No       |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Azure App Insights connection string      | No       |

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs <container-id>

# Or for Azure
az webapp log tail --name your-app-name --resource-group your-rg
```

### Can't connect to Azure OpenAI

- Verify API key and endpoint in environment variables
- Check firewall rules on Azure OpenAI resource
- Ensure deployment names match actual deployments

### RAG index not loading

```bash
# Rebuild the index
curl -X POST http://localhost:8000/rebuild-index

# Or in Azure
curl -X POST https://your-app-name.azurewebsites.net/rebuild-index
```

## Next Steps

- Review [AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md) for detailed deployment guide
- Configure Azure Monitor for logging and alerts
- Set up CI/CD with GitHub Actions
- Enable auto-scaling based on load

## Support

For issues or questions, check:

1. Application logs
2. Azure OpenAI service status
3. Network connectivity
4. API documentation at `/docs` endpoint
