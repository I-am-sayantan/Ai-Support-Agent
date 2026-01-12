"""
Logging configuration for Azure Monitor integration
"""

import logging
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler

def setup_logging():
    """Configure logging with Azure Application Insights"""
    
    # Get connection string from environment
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler for local development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Azure Application Insights handler (if configured)
    if connection_string:
        try:
            azure_handler = AzureLogHandler(
                connection_string=connection_string
            )
            azure_handler.setLevel(logging.INFO)
            logger.addHandler(azure_handler)
            logger.info("Azure Application Insights logging enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize Azure logging: {e}")
    else:
        logger.info("Azure Application Insights not configured (APPLICATIONINSIGHTS_CONNECTION_STRING not set)")
    
    return logger

def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(name)
