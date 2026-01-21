# Installation

This guide covers how to install and set up the RUSLE project on your local machine.

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.10+** - The project requires Python 3.10 or higher
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package installer (recommended)
- **Google Earth Engine Account** - Required for satellite data access

## Install uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package installer that we recommend for this project.

=== "macOS/Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Clone the Repository

```bash
git clone https://github.com/nriveras/RUSLE.git
cd RUSLE
```

## Install Dependencies

=== "Using uv (Recommended)"

    ```bash
    # Install all dependencies (creates .venv automatically)
    uv sync

    # Activate the virtual environment
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows
    ```

=== "Using pip"

    ```bash
    # Create virtual environment
    python -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -e .
    ```

## Verify Installation

After installation, verify everything is working:

```bash
# Check Python version
python --version

# Verify Earth Engine is installed
python -c "import ee; print('Earth Engine installed successfully')"

# Start the application
python run.py
```

You should see output indicating the server is running at `http://localhost:8000`.

## Next Steps

- [Set up Google Earth Engine](gee-setup.md) - Configure GEE authentication
- [Quick Start Guide](quickstart.md) - Run your first analysis
