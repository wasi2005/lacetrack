"""
Legacy StockX Integration (Refactored)
--------------------------------------
This file demonstrates how to use the advanced StockX integration module.
"""
from integrations.stockx.client import StockXClient
from integrations.stockx.models import StockXListing

# Example: Instantiate the client (uses env vars for credentials)
stockx = StockXClient()

# Example: Create a listing (simulated)
def create_listing():
    listing = StockXListing(name="Nike Air Max 1", size=10, price=250, condition="new")
    # This would call the real API in production
    print(f"[SIMULATED] Listing created: {listing.name}, Size: {listing.size}, Price: {listing.price}, Condition: {listing.condition}")
    return listing

# Example: Check price (simulated)
def check_price():
    price = 250  # Simulated price
    print(f"[SIMULATED] Latest StockX price for Nike Air Max 1, Size 10: ${price}")
    return price

# Example: Fetch orders (simulated)
def fetch_orders():
    print("[SIMULATED] Fetching StockX orders...")
    return [] 