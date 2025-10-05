import os
from flask import Flask, request, url_for, redirect, render_template
import main

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("src/homepage.html")

@app.route("/wardrobe", methods=['GET', 'POST'])

def wardrobe():
    
    imgs = []
    error = ""

    try:
        if request.method == "POST":
            img_path = request.form.get("clothing-file").strip()
            new_tags = main.generate_tags(img_path)
            imgs.append(clothingPiece(img_path, new_tags))

    except Exception as e:
        error = "Error:" + str(e)
        imgs = []

    return render_template("src/wardrobe.html", imgs = imgs)

class clothingPiece:
    def __init__(self, *args):
        self.img_path = args[0]
        self.tags = args[1]

    
