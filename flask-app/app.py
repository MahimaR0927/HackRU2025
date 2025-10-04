from flask import Flask, request, url_for, redirect, render_template
import main

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("src/homepage.html")

@app.route("/wardrobe", methods=['GET', 'POST'])

def wardrobe():
    return render_template("src/wardrobe.html")


def addTags(image_path):
    return main.generate_tags(image_path)
