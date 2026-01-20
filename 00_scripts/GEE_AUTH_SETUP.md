# Google Earth Engine Authentication Setup

This project uses automated and persistent GEE authentication. Credentials are stored locally and reused across sessions.

## Quick Start

```python
from gee_auth import initialize_gee

# This handles everything automatically
initialize_gee()
```

## First-Time Setup

1. **Run the notebook or script** - Authentication will be triggered automatically
2. **A browser window will open** - Sign in with your Google account
3. **Authorize Earth Engine** - Grant the necessary permissions
4. **Credentials are saved** - Located at `~/.config/earthengine/credentials`

## With a GEE Cloud Project (Recommended)

If you have a Google Cloud Project with Earth Engine enabled:

```python
from gee_auth import setup_project

# Run once to save your project configuration
setup_project('your-gee-project-id')
```

This saves your project ID to `.gee_config.json` (gitignored) so you don't need to specify it each time.

## Available Functions

### `initialize_gee(project=None, force_auth=False, high_volume=False)`
Main function to initialize GEE with automatic authentication.

```python
# Basic usage
initialize_gee()

# With specific project
initialize_gee(project='my-gee-project')

# Force re-authentication
initialize_gee(force_auth=True)

# Use high-volume endpoint for heavy processing
initialize_gee(high_volume=True)
```

### `print_auth_status()`
Check your current authentication status.

```python
from gee_auth import print_auth_status
print_auth_status()
```

Output:
```
==================================================
Google Earth Engine Authentication Status
==================================================
Credentials file: /Users/you/.config/earthengine/credentials
Credentials exist: ✓ Yes
Authenticated: ✓ Yes
Project configured: ✓ Yes
Project ID: your-project-id
==================================================
```

### `setup_project(project)`
Save your GEE Cloud Project ID for this workspace.

```python
from gee_auth import setup_project
setup_project('your-gee-project-id')
```

### `clear_credentials()`
Remove stored credentials (useful for switching accounts).

```python
from gee_auth import clear_credentials
clear_credentials()
```

## Troubleshooting

### "Earth Engine is not ready to use"
Run `initialize_gee(force_auth=True)` to re-authenticate.

### "Please specify a project"
GEE now requires a Cloud Project. Either:
1. Run `setup_project('your-project-id')` once
2. Or pass it directly: `initialize_gee(project='your-project-id')`

### Creating a GEE Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Earth Engine API
4. Register your project at [Earth Engine](https://code.earthengine.google.com/)

## File Locations

| File | Location | Description |
|------|----------|-------------|
| Credentials | `~/.config/earthengine/credentials` | OAuth tokens (auto-created) |
| Project Config | `.gee_config.json` | Project ID for this workspace |
| Auth Module | `00_scripts/gee_auth.py` | Authentication helper functions |

## Security Notes

- **Never commit credentials** - They're stored outside the repo
- **`.gee_config.json` is gitignored** - Project IDs stay private
- **Use service accounts for production** - Better for automated workflows
