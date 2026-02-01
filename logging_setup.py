"""Centralized logging configuration for the application."""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s:%(lineno)d %(message)s"
)
