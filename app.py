from flask import Flask, redirect, render_template, request, url_for, jsonify
from service.userservice import login_service
# Initialize the Flask application
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/submit", methods=["POST"])
def submit():
    email = request.form.get('Email')
    user = login_service(email)
    return jsonify(user)

# only run the app if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)