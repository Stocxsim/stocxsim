from flask import Blueprint, request, jsonify, render_template
from service.stockservice import search_stocks_service, get_stock_detail_service

stock_bp = Blueprint("stock_bp", __name__)


@stock_bp.route("/search")
def search_stocks():
     query = request.args.get("q", "").strip()

     if not query:
          return jsonify([])

     return jsonify(search_stocks_service(query))


@stock_bp.route("/<stock_token>")
def stock_detail(stock_token):
    stock = get_stock_detail_service(stock_token)

    if not stock:
        return render_template("404.html"), 404

    return render_template("stock.html", stock=stock)