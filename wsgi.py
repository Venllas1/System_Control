import logging
from app import create_app

# System Logging for Vercel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Create Flask application instance
    application = create_app()
    logger.info("✓ Application initialized successfully")
except Exception as e:
    logger.error(f"✗ CRITICAL STARTUP ERROR: {str(e)}")
    raise

# Vercel expects 'app' variable
app = application
