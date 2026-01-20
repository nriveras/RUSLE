"""
Google Earth Engine Authentication Helper.

This module provides functions for automated and persistent GEE authentication.
Credentials are stored locally and reused across sessions.

Usage:
    from gee_auth import initialize_gee
    initialize_gee()  # Handles auth automatically
"""

import json
import os
from pathlib import Path
from typing import Optional

import ee


# =============================================================================
# Configuration
# =============================================================================

# Default credentials directory (follows GEE convention)
DEFAULT_CREDENTIALS_DIR = Path.home() / '.config' / 'earthengine'
CREDENTIALS_FILE = 'credentials'

# Project configuration file for this workspace
PROJECT_CONFIG_FILE = Path(__file__).parent.parent / '.gee_config.json'


# =============================================================================
# Authentication Functions
# =============================================================================

def get_credentials_path() -> Path:
    """
    Get the path to the GEE credentials file.

    Returns:
        Path: Path to credentials file.
    """
    return DEFAULT_CREDENTIALS_DIR / CREDENTIALS_FILE


def credentials_exist() -> bool:
    """
    Check if GEE credentials file exists.

    Returns:
        bool: True if credentials file exists, False otherwise.
    """
    return get_credentials_path().exists()


def is_authenticated() -> bool:
    """
    Check if GEE is properly authenticated.

    Returns:
        bool: True if authenticated and can connect to GEE.
    """
    if not credentials_exist():
        return False

    try:
        ee.Initialize()
        # Test connection with a simple operation
        ee.Number(1).getInfo()
        return True
    except Exception:
        return False


def authenticate(force: bool = False) -> bool:
    """
    Authenticate with Google Earth Engine.

    This function will:
    1. Check if valid credentials exist
    2. If not (or force=True), trigger interactive authentication
    3. Store credentials for future sessions

    Args:
        force: If True, force re-authentication even if credentials exist.

    Returns:
        bool: True if authentication successful, False otherwise.
    """
    if force:
        # Clear old credentials before re-authenticating
        clear_credentials()
    
    print("Authenticating with Google Earth Engine...")
    print("A browser window will open for authentication.\n")

    try:
        # Force new authentication flow
        ee.Authenticate(force=True)
        print("\n✓ Authentication successful! Credentials saved.")
        return True
    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        return False


def initialize_gee(
    project: Optional[str] = None,
    force_auth: bool = False,
    high_volume: bool = False
) -> bool:
    """
    Initialize Google Earth Engine with automatic authentication.

    This is the main function to use. It handles:
    1. Checking for existing credentials
    2. Authenticating if needed
    3. Initializing the EE API

    Args:
        project: GEE Cloud Project ID (optional but recommended).
        force_auth: Force re-authentication even if credentials exist.
        high_volume: Use high-volume endpoint for heavy processing.

    Returns:
        bool: True if initialization successful, False otherwise.

    Example:
        >>> from gee_auth import initialize_gee
        >>> initialize_gee(project='my-gee-project')
        ✓ Google Earth Engine initialized successfully
        True
    """
    # Load project from config if not provided
    if project is None:
        project = load_project_config()

    # Authenticate if needed
    if force_auth or not credentials_exist():
        if not authenticate(force=force_auth):
            return False

    # Initialize Earth Engine
    try:
        init_kwargs = {}

        if project:
            init_kwargs['project'] = project

        if high_volume:
            init_kwargs['opt_url'] = 'https://earthengine-highvolume.googleapis.com'

        ee.Initialize(**init_kwargs)

        # Verify connection
        ee.Number(1).getInfo()

        project_msg = f" (project: {project})" if project else ""
        print(f"✓ Google Earth Engine initialized successfully{project_msg}")
        return True

    except Exception as e:
        error_msg = str(e).lower()
        
        # Handle expired/invalid credentials
        if 'invalid_grant' in error_msg or 'bad request' in error_msg:
            print("⚠ Stored credentials are expired or invalid. Re-authenticating...")
            clear_credentials()
            if authenticate(force=True):
                # Try initialization again after fresh authentication
                return initialize_gee(project=project, force_auth=False, high_volume=high_volume)
            return False
        
        # Handle project errors
        elif "not registered" in str(e) or "project" in error_msg:
            print(f"✗ Initialization failed: {e}")
            if "not registered" in str(e) and project:
                print(f"\n⚠ ACTION REQUIRED: Project '{project}' is not registered.")
                print(f"➜ Register it here: https://console.cloud.google.com/earth-engine/configuration?project={project}")
            elif "permission" in error_msg:
                print("\n⚠ Check project permissions in Google Cloud Console.")
            else:
                print("\nTip: Ensure you have a valid GEE Cloud Project ID set.")
            return False
        
        else:
            print(f"✗ Initialization failed: {e}")
            return False


# =============================================================================
# Project Configuration
# =============================================================================

def save_project_config(project: str) -> None:
    """
    Save GEE project ID to local config file.

    Args:
        project: GEE Cloud Project ID.
    """
    config = {'project': project}
    with open(PROJECT_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✓ Project configuration saved to {PROJECT_CONFIG_FILE}")


def load_project_config() -> Optional[str]:
    """
    Load GEE project ID from local config file.

    Returns:
        str or None: Project ID if config exists, None otherwise.
    """
    if PROJECT_CONFIG_FILE.exists():
        try:
            with open(PROJECT_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('project')
        except (json.JSONDecodeError, IOError):
            return None
    return None


def setup_project(project: str) -> bool:
    """
    Set up GEE project for this workspace.

    This saves the project ID locally so you don't need to specify it
    each time you initialize GEE.

    Args:
        project: GEE Cloud Project ID.

    Returns:
        bool: True if setup successful.
    """
    save_project_config(project)
    return initialize_gee(project=project)


# =============================================================================
# Utility Functions
# =============================================================================

def get_auth_status() -> dict:
    """
    Get detailed authentication status.

    Returns:
        dict: Authentication status information.
    """
    status = {
        'credentials_exist': credentials_exist(),
        'credentials_path': str(get_credentials_path()),
        'is_authenticated': False,
        'project_configured': load_project_config() is not None,
        'project': load_project_config()
    }

    if status['credentials_exist']:
        status['is_authenticated'] = is_authenticated()

    return status


def print_auth_status() -> None:
    """Print a formatted authentication status report."""
    status = get_auth_status()

    print("=" * 50)
    print("Google Earth Engine Authentication Status")
    print("=" * 50)
    print(f"Credentials file: {status['credentials_path']}")
    print(f"Credentials exist: {'✓ Yes' if status['credentials_exist'] else '✗ No'}")
    print(f"Authenticated: {'✓ Yes' if status['is_authenticated'] else '✗ No'}")
    print(f"Project configured: {'✓ Yes' if status['project_configured'] else '✗ No'}")
    if status['project']:
        print(f"Project ID: {status['project']}")
    print("=" * 50)


def clear_credentials() -> None:
    """
    Remove stored GEE credentials.

    Use this if you need to re-authenticate with a different account.
    """
    cred_path = get_credentials_path()
    if cred_path.exists():
        cred_path.unlink()
        print("✓ Credentials removed. You will need to re-authenticate.")
    else:
        print("No credentials file found.")


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == '__main__':
    print_auth_status()
