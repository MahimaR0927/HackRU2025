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

    try:
        if request.method == "POST":

            if 'clothing-file' not in request.files:
                print('No file part')

            UPLOAD_FOLDER = 'templates/src/images' # Replace with your desired path
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

            file = request.files['clothing-file']

            # If the user does not select a file, the browser submits an empty file without a filename.
            if file.filename == '':
                print('No selected file')

            if file:
                filename = file.filename
                
                # This is the key step: Save the image data to your server's file system
                file_path_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path_on_server)
                
                # Now you have the file and its path on the server
                print(f'File uploaded successfully to: {file_path_on_server}')
                imgs.append(clothingPiece(filename, main.generate_tags(file_path_on_server)))
                print(imgs[-1])

        
    except Exception as e:
        print(str(e))
        imgs = []

    return render_template("src/wardrobe.html", imgs = imgs)    



class clothingPiece:
    def __init__(self, *args):
        self.img_path = args[0]
        self.tags = args[1]

    def __str__(self):
        return self.img_path + ":" + " ".join(self.tags)

    
