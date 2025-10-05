import os
import json # Only needed if you plan to use jsonify in the future, currently commented out
from flask import Flask, request, render_template, jsonify
import main # Keep this if you use main.generate_tags later
from pymongo import MongoClient
from werkzeug.utils import secure_filename

MONGO_URI = "mongodb+srv://mahimar0927:jqIIIk3sxoUMTqkV@cluster0.d0oisrw.mongodb.net/" 
DB_NAME = "Outfits_db"
COLLECTION_NAME = "choices"

app = Flask(__name__)

# 1.2 Local File Storage Path: HACKRU/flask-app/static/images
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"Upload folder path: {app.config['UPLOAD_FOLDER']}")

# 1.3 Initialize MongoDB Connection
client = None
collection = None
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    client.admin.command('ping') 
    print("Successfully connected to MongoDB Atlas.")
except Exception as e:
    print("-" * 50)
    print("!!! MONGODB CONNECTION FAILED !!!")
    print(f"Error Details: {e}")
    print("!!! The application will run, but database operations will fail. !!!")
    print("-" * 50)


class clothingPiece:
    """Class to hold clothing item data fetched from the database."""
    def __init__(self, img_path, tags):
        # img_path will be the filename (e.g., 'shirt.jpg') for static access
        self.img_path = img_path
        # Ensures tags is always a list for the Jinja template's '|join' filter
        self.tags = tags.split(', ') if isinstance(tags, str) else tags

@app.route("/")
def index():
    """Renders the login."""
    return render_template("src/login.html")

@app.route("/homepage")
def homepage():
    """Renders the homepage."""
    return render_template("src/homepage.html")


@app.route("/outfits")
def outfits():
    return render_template("src/outfits.html")

@app.route("/wardrobe", methods=['GET', 'POST'])
def wardrobe():
    current_imgs = []

    # --- POST request logic: Handle file upload, save locally, and insert into DB ---
    if request.method == "POST":
        if collection is None:
            # Respond with JSON error as expected by the frontend 'fetch' call
            return jsonify({"error": "Database connection not established."}), 500

        # Get ALL files sent under the 'clothing_file' key
        uploaded_files = request.files.getlist('clothing_file')

        if not uploaded_files:
            return jsonify({"error": "No files received for upload."}), 400

        items_to_insert = []
        
        for i, file in enumerate(uploaded_files):
            # Get the corresponding tag using the index (e.g., tag_0, tag_1)


            #tag_key = f'tag_{i}'
            #tag_string = request.form.get(tag_key, 'No Tag').strip()
            
            # 1. Secure filename and define the full local path
            filename = secure_filename(file.filename)

            # The file is saved to the UPLOAD_FOLDER (static/images)
            file_path_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                # 2. Save the file to the 'static/images' folder
                file.save(file_path_on_server) 
                tag_string = main.generate_tags(file_path_on_server)

                # NOTE: If you integrate main.generate_tags, place the call here:
                # new_tags = main.generate_tags(file_path_on_server)
                # tag_string = f"{tag_string}, {new_tags}" 
                
                # 3. Prepare data for MongoDB
                item_data = {
                    # Store the tag string
                    "tags": tag_string, 
                    # Store only the filename, as this is all the template needs for static access
                    "filename": filename 
                }
                items_to_insert.append(item_data)
                
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                # Return an error for the frontend 'fetch' call
                return jsonify({"error": f"Failed to save file {filename} locally."}), 500
        
        # 4. Insert all items into MongoDB Atlas
        if items_to_insert:
            try:
                collection.insert_many(items_to_insert)
                # Return success for the frontend 'fetch' call
                return jsonify({"message": f"Uploaded {len(items_to_insert)} items."}), 200
            except Exception as e:
                print(f"Error inserting into MongoDB: {e}")
                return jsonify({"error": "Files saved locally but failed to update database."}), 500
  
    if collection is not None:
        try:
            # Fetch all items from the database
            for item in collection.find(): 
                # The filename is used as the img_path for the clothingPiece object
                current_imgs.append(clothingPiece(item.get('filename'), item.get('tags', 'No Tag')))
        except Exception as e:
            print(f"Error fetching data from MongoDB: {e}")
            
    # Render the template, passing the list of items
    return render_template("src/wardrobe.html", imgs=current_imgs)


if __name__ == "__main__":
    app.run(debug=True)