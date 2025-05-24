"""
Logging module for the LangChain and Streamlit application.

This module sets up logging configuration for the application with:
- INFO, WARNING, and ERROR levels
- File logging to logs/errors/error.log
- Console output for immediate feedback
- Automatic creation of log directories
"""

import os
import logging
from logging.handlers import RotatingFileHandler
import csv
from datetime import datetime

# Constants
LOG_DIR = os.path.join("logs", "errors")
LOG_FILE = os.path.join(LOG_DIR, "error.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
CONVERSAS_CSV_PATH = os.path.join("logs", "conversas.csv")

# Create logger instance
logger = logging.getLogger("estudamais")
logger.setLevel(logging.INFO)

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Create file handler with rotation (10MB max size, keep 5 backup logs)
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10_000_000, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Convenience functions
def info(message):
    """Log an info level message"""
    logger.info(message)


def warning(message):
    """Log a warning level message"""
    logger.warning(message)


def error(message, exc_info=False):
    """
    Log an error level message, optionally with exception info

    Args:
        message: The error message
        exc_info: If True, include exception traceback information
    """
    logger.error(message, exc_info=exc_info)


# Cria o cabeçalho do CSV se o arquivo não existir
if not os.path.exists(CONVERSAS_CSV_PATH):
    # Ensure the 'logs' directory itself exists
    os.makedirs(os.path.dirname(CONVERSAS_CSV_PATH), exist_ok=True)
    with open(CONVERSAS_CSV_PATH, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Score", "Pergunta", "Resposta"])


def log_conversa(score, pergunta, resposta):
    """Loga a conversa em CSV com timestamp, score, pergunta e resposta"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CONVERSAS_CSV_PATH, mode="a", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                timestamp,
                round(score, 4) if score is not None else "N/A",
                pergunta,
                resposta,
            ]
        )
