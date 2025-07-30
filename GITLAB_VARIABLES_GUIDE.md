# GitLab CI/CD Variables and Configuration Guide

## 🎯 **Required GitLab CI/CD Variables**

### **🔐 Kubernetes Access Variables**

| Variable Name | Description | Example | Required |
|---------------|-------------|---------|----------|
| `KUBE_CONFIG` | Base64 encoded Kubernetes config file | `base64 -w 0 ~/.kube/config` | ✅ Yes |
| `CI_REGISTRY` | GitLab container registry URL | `registry.gitlab.com` | ✅ Yes |
| `CI_DEPLOY_USER` | GitLab deploy token username | `gitlab+deploy-token-123` | ✅ Yes |
| `CI_DEPLOY_PASSWORD` | GitLab deploy token password | `your-deploy-token-password` | ✅ Yes |

### **🤖 AI Service Variables (Optional)**

| Variable Name | Description | Example | Required |
|---------------|-------------|---------|----------|
| `GEMINI_API_KEY_B64` | Base64 encoded Gemini API key | `echo -n "your-key" \| base64` | ❌ No |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | `https://hooks.slack.com/...` | ❌ No |

### **🏗️ Build Variables (Auto-generated)**

| Variable Name | Description | Source | Required |
|---------------|-------------|--------|----------|
| `CI_REGISTRY_IMAGE` | GitLab registry image path | Auto | ✅ Yes |
| `CI_COMMIT_REF_SLUG` | Branch/tag name | Auto | ✅ Yes |
| `CI_COMMIT_SHA` | Commit hash | Auto | ✅ Yes |
| `CI_JOB_TOKEN` | Job authentication token | Auto | ✅ Yes |

## 🔧 **How to Set GitLab Variables**

### **Step 1: Access GitLab Project Settings**
```
Project → Settings → CI/CD → Variables
```

### **Step 2: Add Required Variables**

#### **KUBE_CONFIG (Required)**
```bash
# Generate base64 encoded kubeconfig
base64 -w 0 ~/.kube/config
```
- **Key**: `KUBE_CONFIG`
- **Value**: Output from above command
- **Type**: Variable
- **Protected**: ✅ Yes
- **Masked**: ✅ Yes

#### **GitLab Deploy Token (Required)**
```bash
# Create deploy token in GitLab
Project → Settings → Repository → Deploy Tokens
```
- **Key**: `CI_DEPLOY_USER`
- **Value**: `gitlab+deploy-token-<ID>`
- **Type**: Variable
- **Protected**: ✅ Yes
- **Masked**: ❌ No

- **Key**: `CI_DEPLOY_PASSWORD`
- **Value**: Deploy token password
- **Type**: Variable
- **Protected**: ✅ Yes
- **Masked**: ✅ Yes

#### **AI API Keys (Optional)**
```bash
# For Gemini API key
echo -n "your-gemini-api-key" | base64
```
- **Key**: `GEMINI_API_KEY_B64`
- **Value**: Base64 encoded API key
- **Type**: Variable
- **Protected**: ✅ Yes
- **Masked**: ✅ Yes

#### **Slack Integration (Optional)**
- **Key**: `SLACK_WEBHOOK_URL`
- **Value**: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
- **Type**: Variable
- **Protected**: ✅ Yes
- **Masked**: ❌ No

## 📋 **config.env vs GitLab Variables**

### **🎯 Purpose of config.env**

The `config.env` file serves **two different purposes**:

#### **1. Local Development**
```bash
# Used when running locally
uv run python server.py
# or
uv run python -m mcp_client_tools.professional_ui
```

#### **2. Docker Container Environment**
```dockerfile
# Referenced in Dockerfile
COPY config.env /app/config.env
```

### **🔄 Variable Priority (Highest to Lowest)**

1. **GitLab CI/CD Variables** (Production)
2. **Kubernetes Secrets** (Production)
3. **config.env** (Local/Docker)
4. **Default values** (Code)

## 📁 **config.env Configuration**

### **Current config.env Structure:**
```bash
# AI API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
MCP_SERVER_URL=http://127.0.0.1:9000
WEB_UI_PORT=9090
WEB_UI_HOST=127.0.0.1

# Slack Integration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### **🔧 How config.env is Used**

#### **In server.py:**
```python
# Load environment variables
load_dotenv('config.env')
```

#### **In professional_ui.py:**
```python
# Load config for AI service
def load_env_config():
    load_dotenv('config.env')
```

#### **In Dockerfile:**
```dockerfile
# Copy config file
COPY config.env /app/config.env
```

## 🚀 **Deployment Flow**

### **Local Development:**
```
config.env → Application
```

### **GitLab CI/CD:**
```
GitLab Variables → Kubernetes Secrets → Application
```

### **Production:**
```
Kubernetes Secrets → Application
```

## 📊 **Variable Mapping**

| Environment | Source | Example |
|-------------|--------|---------|
| **Local** | `config.env` | `GEMINI_API_KEY=your-key` |
| **GitLab CI** | GitLab Variables | `GEMINI_API_KEY_B64=base64-key` |
| **Kubernetes** | Secrets | `GEMINI_API_KEY_B64` in Secret |
| **Container** | Environment | `GEMINI_API_KEY` from Secret |

## 🔐 **Security Best Practices**

### **✅ Do This:**
- Use GitLab protected variables for sensitive data
- Mask API keys and passwords
- Use base64 encoding for complex values
- Keep `config.env` out of version control (add to `.gitignore`)

### **❌ Don't Do This:**
- Commit API keys to Git
- Use plain text passwords in variables
- Share sensitive variables publicly
- Use the same keys for dev/prod

## 🎯 **Quick Setup Checklist**

### **Required Variables:**
- [ ] `KUBE_CONFIG` (base64 encoded)
- [ ] `CI_DEPLOY_USER` (deploy token username)
- [ ] `CI_DEPLOY_PASSWORD` (deploy token password)

### **Optional Variables:**
- [ ] `GEMINI_API_KEY_B64` (base64 encoded)
- [ ] `SLACK_WEBHOOK_URL` (Slack webhook)

### **Local Development:**
- [ ] `config.env` configured for local testing
- [ ] `.gitignore` includes `config.env`

## 🎉 **Summary**

- **GitLab Variables**: For production deployment and secrets
- **config.env**: For local development and Docker containers
- **Kubernetes Secrets**: For runtime configuration in production
- **Priority**: GitLab Variables > Kubernetes Secrets > config.env > Defaults

This setup provides flexibility for different environments while maintaining security! 🚀 