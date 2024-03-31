"""
StockX Webhook Endpoint
----------------------
Flask blueprint for handling StockX webhook events.
"""

from flask import Blueprint, request, jsonify

stockx_webhook_bp = Blueprint('stockx_webhook', __name__)

@stockx_webhook_bp.route('/integrations/stockx/webhook', methods=['POST'])
def stockx_webhook():
    """Handle incoming StockX webhook events."""
    data = request.json
    # TODO: process_webhook(data)
    return jsonify({'status': 'received'}) 