from flask import Flask, redirect, render_template, request, url_for, jsonify
from service.userservice import login_service
from routes.user_routes import user_bp

# Initialize the Flask application
app = Flask(__name__)

app.register_blueprint(user_bp, url_prefix='/login')

@app.route("/")
def home():
    return render_template("home.html")

# only run the app if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)