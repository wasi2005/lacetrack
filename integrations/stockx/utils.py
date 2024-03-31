"""
StockX Utilities
----------------
Helper functions for StockX integration.
"""

import logging

def get_logger():
    """Get a logger for StockX integration."""
    return logging.getLogger('stockx')

def format_price(price):
    """Format price as USD string."""
    return f"${price:,.2f}" 