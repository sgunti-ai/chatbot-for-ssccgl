#!/usr/bin/env python3
"""
SSC RAG Backend - Main Entry Point
Run this file to start the FastAPI backend server
"""

import os
import uvicorn
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend.log')
    ]
)

logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info("Loaded environment variables from .env file")
    else:
        logger.warning(".env file not found. Using system environment variables")

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_REGION'
    ]
    
    optional_vars = [
        'PINECONE_API_KEY',  # Optional if using ChromaDB
        'CHROMA_HOST',
        'CHROMA_PORT'
    ]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        logger.error(f"Missing required environment variables: {', '.join(missing_required)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    # Check for at least one vector database configuration
    if not os.getenv('PINECONE_API_KEY') and not os.getenv('CHROMA_HOST'):
        logger.warning("No vector database configuration found. Using local ChromaDB.")
    
    logger.info("Environment check passed")
    return True

def create_app():
    """Create and return the FastAPI application"""
    try:
        from app.main import app
        logger.info("FastAPI application created successfully")
        return app
    except ImportError as e:
        logger.error(f"Failed to import application: {e}")
        raise
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise

def main():
    """Main function to run the backend server"""
    print("""
    ┌──────────────────────────────────────────────────────────┐
    │                 SSC RAG Backend Server                   │
    │             Question Search & Processing API             │
    └──────────────────────────────────────────────────────────┘
    """)
    
    # Load environment variables
    load_environment()
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed. Exiting.")
        return
    
    # Create application
    try:
        app = create_app()
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        return
    
    # Get server configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    reload = os.getenv('RELOAD', 'false').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Reload mode: {reload}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Print available endpoints
    print(f"\n📡 Server starting at: http://{host}:{port}")
    print("🔍 API Documentation: http://localhost:8000/docs")
    print("📚 ReDoc Documentation: http://localhost:8000/redoc")
    print("\nAvailable endpoints:")
    print("  GET  /                    - API information")
    print("  POST /query               - Search similar questions")
    print("  POST /process-file        - Upload and process question paper")
    print("  POST /process-text        - Process text content")
    print("  GET  /subjects            - List available subjects")
    print("  GET  /health              - Health check")
    print("  GET  /stats               - System statistics")
    print("  POST /questions           - Create manual question")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    main()
