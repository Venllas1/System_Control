import logging
from app import create_app

# System Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    app = create_app()
    logger.info("Application initialized successfully")
except Exception as e:
    logger.error(f"CRITICAL STARTUP ERROR: {str(e)}")
    raise
