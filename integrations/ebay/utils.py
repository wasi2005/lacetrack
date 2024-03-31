"""
eBay Utilities
--------------
Helper functions for eBay integration.
"""

import logging

def get_logger():
    """Get a logger for eBay integration."""
    return logging.getLogger('ebay')

def format_price(price):
    """Format price as USD string."""
    return f"${price:,.2f}" 