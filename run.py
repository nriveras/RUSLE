#!/usr/bin/env python
"""
RUSLE Web Application Entry Point.

Usage:
    python run.py [--host HOST] [--port PORT] [--reload]
    
Options:
    --host HOST     Host to bind to (default: 0.0.0.0)
    --port PORT     Port to bind to (default: 8000)
    --reload        Enable auto-reload for development
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Run the RUSLE web application")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is not installed. Run: uv pip install uvicorn")
        sys.exit(1)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                 RUSLE Soil Loss Calculator                       ║
║                      Web Application                             ║
╠══════════════════════════════════════════════════════════════════╣
║  Starting server at http://{args.host}:{args.port}                          ║
║  Open http://localhost:{args.port}/app in your browser                 ║
║                                                                  ║
║  Press Ctrl+C to stop                                            ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
