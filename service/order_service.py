from database.order_dao import get_order

def get_order_details(user_id,filter_params):
    return get_order(user_id,filter_params)