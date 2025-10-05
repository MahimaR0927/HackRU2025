import os
from flask import Flask, request, url_for, redirect, render_template
import main
from pymongo import MongoClient


app = Flask(__name__)




@app.route("/")
def index():
   return render_template("src/homepage.html")


@app.route("/wardrobe", methods=['GET', 'POST'])


def wardrobe():
  
   imgs = []
   error = ""


except Exception as e:
    error = "Error:" + str(e)
    imgs = []


class clothingPiece:
   def __init__(self, *args):
       self.img_path = args[0]
       self.tags = args[1]


  
