from flask import Flask, render_template,session
from service.userservice import login_service
from routes.user_routes import user_bp
from routes.stock_routes import stock_bp

app = Flask(__name__)
app.secret_key = "an12eadf234f" 

app.register_blueprint(user_bp, url_prefix='/login')
app.register_blueprint(stock_bp, url_prefix='/stocks')

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)