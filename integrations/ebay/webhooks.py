"""
eBay Webhook Endpoint
---------------------
Flask blueprint for handling eBay webhook events.
"""

from flask import Blueprint, request, jsonify

ebay_webhook_bp = Blueprint('ebay_webhook', __name__)

@ebay_webhook_bp.route('/integrations/ebay/webhook', methods=['POST'])
def ebay_webhook():
    """Handle incoming eBay webhook events."""
    data = request.json
    # TODO: process_webhook(data)
    return jsonify({'status': 'received'}) 