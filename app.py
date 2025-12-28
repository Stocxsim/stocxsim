from flask import Flask, redirect, render_template, request, url_for, jsonify



# Initialize the Flask application
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")



# only run the app if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True)