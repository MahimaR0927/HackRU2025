from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("src/homepage.html")

@app.route("/wardrobe")
def wardrobe():
    return render_template("src/wardrobe.html")