"""
StockX Data Models
------------------
Defines data structures for StockX listings and orders.
"""

class StockXListing:
    """Represents a sneaker listing on StockX."""
    def __init__(self, name, size, price, condition, sku=None, listing_id=None):
        self.name = name
        self.size = size
        self.price = price
        self.condition = condition
        self.sku = sku
        self.listing_id = listing_id

class StockXOrder:
    """Represents an order on StockX."""
    def __init__(self, order_id, listing_id, status, price, buyer_info=None):
        self.order_id = order_id
        self.listing_id = listing_id
        self.status = status
        self.price = price
        self.buyer_info = buyer_info 