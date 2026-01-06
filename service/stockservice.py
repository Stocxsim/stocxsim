from database.stockdao import search_stocks, get_stock_by_token
from modal.Stock import Stock

# Service function to search stocks
def search_stocks_service(query):
     rows = search_stocks(query)

     return [
          {
               "token": row[0],
               "name": row[1]
          }
          for row in rows
     ]

# New service function to get stock details by symbol
def get_stock_detail_service(stock_token):
    row = get_stock_by_token(stock_token)

    if not row:
        return None

    return Stock(
        stock_token=row[0],
        stock_name=row[1]
    )