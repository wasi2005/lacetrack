# eBay Integration

This module handles all eBay-related functionality, including:
- OAuth2 authentication
- Listing management (create, update, delete)
- Order management (fetch, update, sync)
- Price monitoring and history
- Webhook endpoint for real-time updates
- Background jobs for periodic sync

## Structure
- `client.py`: API client logic
- `models.py`: Data models for listings and orders
- `tasks.py`: Background jobs (sync, webhooks)
- `webhooks.py`: Flask blueprint for webhook endpoint
- `utils.py`: Helper functions 