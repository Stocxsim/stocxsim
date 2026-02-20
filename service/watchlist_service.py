"""
service/watchlist_service.py
-----------------------------
Business logic for adding, removing, and checking watchlist stocks.

Key rule: Index tokens (NIFTY, SENSEX, etc.) are NEVER added to the watchlist.
They are shown separately in the top-of-page ticker and must be excluded here.
"""

from database.watchlist_dao import add_to_watchlist, remove_from_watchlist, check_watchlist
from database.watchlist_dao import get_stock_tokens_by_user

from utils.tokens import INDEX_TOKENS



def get_watchlist_tokens(user_id):
    """Return all watchlist token-category pairs for a user (raw DB rows)."""
    return get_stock_tokens_by_user(user_id)



def toggle_watchlist(user_id, stock_token):
    """
    Toggle a stock's watchlist membership for a given user.

    - If the token is an index (NIFTY/SENSEX), it is removed silently and
      False is returned (indices should never be watchlisted).
    - If the stock is already watchlisted, it is removed and False returned.
    - If not watchlisted, it is added and True returned.

    Returns:
        bool: True if now watchlisted, False if removed.
    """
    token_str = str(stock_token)
    if token_str in INDEX_TOKENS:
        # Indices are not allowed in watchlist.
        if check_watchlist(user_id, token_str):
            remove_from_watchlist(user_id, token_str)
        return False

    if check_watchlist(user_id, stock_token):
        remove_from_watchlist(user_id, stock_token)
        return False
    else:
        add_to_watchlist(user_id, stock_token)
        return True



def is_in_watchlist(user_id, stock_token):
    """
    Check whether a given stock is in the user's watchlist.

    Returns:
        bool: True if watchlisted, False otherwise.
    """
    return check_watchlist(user_id, stock_token)
