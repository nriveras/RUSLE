# Google Earth Engine Setup

Google Earth Engine (GEE) provides access to satellite imagery and geospatial datasets required for RUSLE calculations. This guide covers authentication and project setup.

## Prerequisites

1. A Google account
2. Access to Google Earth Engine (sign up at [earthengine.google.com](https://earthengine.google.com/signup/))
3. A Google Cloud Project with the Earth Engine API enabled

## Create a GEE Project

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Create Project**
3. Enter a project name (e.g., `rusle-analysis`)
4. Click **Create**

### Step 2: Enable Earth Engine API

1. In the Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Earth Engine API"
3. Click **Enable**

### Step 3: Register for Earth Engine

1. Go to [earthengine.google.com/signup](https://earthengine.google.com/signup/)
2. Sign in with your Google account
3. Complete the registration form
4. Wait for approval (usually instant for personal use)

## Authentication

### Local Development

For local development, authenticate using the command line:

```bash
# Authenticate with Earth Engine
earthengine authenticate

# Set your default project
earthengine set_project your-project-id
```

This opens a browser window for Google authentication and stores credentials in `~/.config/earthengine/`.

### Environment Configuration

Create a `.env` file in the project root:

```bash
# .env
RUSLE_GEE_PROJECT=your-project-id
RUSLE_DEBUG=true
```

!!! tip "Project ID Format"
    The project ID is usually in the format `ee-username` or `your-project-name`. You can find it in the Google Cloud Console.

### Docker Deployment

When running in Docker, credentials are mounted from your local machine:

```yaml
# docker-compose.yml
volumes:
  - ~/.config/earthengine:/home/appuser/.config/earthengine:ro
```

!!! warning "Authenticate First"
    You must run `earthengine authenticate` on the host machine before starting the Docker container.

## Verify Connection

Test your GEE connection:

```python
import ee

# Initialize with your project
ee.Authenticate()
ee.Initialize(project='your-project-id')

# Test connection
print(ee.Number(1).getInfo())  # Should print: 1
```

## Troubleshooting

### "Project not registered"

If you see this error:

```
ee.EEException: Project is not registered
```

**Solution**: Register your project at [code.earthengine.google.com](https://code.earthengine.google.com/) and accept the terms of service.

### "Invalid credentials"

If authentication fails:

```bash
# Force re-authentication
earthengine authenticate --force
```

### Rate Limits

GEE has usage quotas. For large analyses:

- Reduce the area of interest
- Increase the export scale (lower resolution)
- Use batch processing for multiple regions

## Next Steps

- [Quick Start Guide](quickstart.md) - Run your first analysis
- [Configuration Reference](../reference/configuration.md) - All configuration options
