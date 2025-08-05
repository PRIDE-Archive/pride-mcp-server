# GitLab CI/CD Variables Configuration

This document describes the GitLab CI/CD variables that need to be configured for the PRIDE MCP Server deployment.

## Required Variables

### Proxy Configuration
These variables are used for internet access during both build and runtime:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `HTTP_PROXY` | HTTP proxy server URL | `http://hx-wwwcache.ebi.ac.uk:3128` |
| `HTTPS_PROXY` | HTTPS proxy server URL | `http://hx-wwwcache.ebi.ac.uk:3128` |
| `http_proxy` | HTTP proxy server URL (lowercase) | `http://hx-wwwcache.ebi.ac.uk:3128` |
| `https_proxy` | HTTPS proxy server URL (lowercase) | `http://hx-wwwcache.ebi.ac.uk:3128` |
| `NO_PROXY` | Comma-separated list of hosts to bypass proxy | `localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,.ebi.ac.uk` |

### API Keys
These variables are used for AI functionality:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `GEMINI_API_KEY` | Google Gemini API key (base64 encoded) | `base64_encoded_api_key_here` |

## How to Set Variables in GitLab

1. Go to your GitLab project
2. Navigate to **Settings** → **CI/CD**
3. Expand the **Variables** section
4. Click **Add Variable** for each variable
5. Set the **Type** to **Variable** (not File)
6. Set **Environment scope** to **All (default)**
7. Check **Protect variable** if needed
8. Check **Mask variable** for sensitive data like API keys

## Default Values

If proxy variables are not set, the system will use these defaults:
- `HTTP_PROXY`: `http://hx-wwwcache.ebi.ac.uk:3128`
- `HTTPS_PROXY`: `http://hx-wwwcache.ebi.ac.uk:3128`
- `NO_PROXY`: `localhost,127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,.ebi.ac.uk`

## Usage

These variables are used in:
- **Docker build**: For downloading Python packages
- **Kubernetes deployment**: For runtime internet access
- **Application**: For making HTTP requests to external APIs

## Testing

After setting the variables, trigger a new pipeline to test the configuration:

```bash
git commit --allow-empty -m "Test proxy configuration"
git push
``` 