from database.watchlist_dao import add_to_watchlist, remove_from_watchlist, check_watchlist
from database.watchlist_dao import get_stock_tokens_by_user

from utils.tokens import INDEX_TOKENS


def get_watchlist_tokens(user_id):
    return get_stock_tokens_by_user(user_id)


def toggle_watchlist(user_id, stock_token):
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
    return check_watchlist(user_id, stock_token)
