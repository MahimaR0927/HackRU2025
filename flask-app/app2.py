import os
import json # Used for JSON response
# Removed unused 'url_for' and 'redirect'
from flask import Flask, request, render_template, jsonify
# import main # Keep this if you plan to use main.generate_tags (currently commented out below)

from pymongo import MongoClient
from werkzeug.utils import secure_filename

# 1. MongoDB Atlas Connection String
# Get this from your Atlas cluster by clicking 'Connect' -> 'Connect your application'
MONGO_URI = "mongodb+srv://mahimar0927:jqIIIk3sxoUMTqkV@cluster0.d0oisrw.mongodb.net/"
DB_NAME = "Outfits_db"
COLLECTION_NAME = "choices"

# 2. Local File Storage Path (Desktop Folder)
UPLOAD_FOLDER_NAME = 'clothing_uploads'
HOME_DIR = os.path.expanduser('~')
UPLOAD_FOLDER = os.path.join(HOME_DIR, 'Desktop', UPLOAD_FOLDER_NAME)

# Create the directory if it doesn't exist (exist_ok=True is key!)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
# Set the upload folder globally for Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize MongoDB Connection
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
    print("-" * 50)


# --- UTILITY CLASS ---

class clothingPiece:
    """Class to hold clothing item data fetched from the database."""
    # Renamed *args to descriptive names for clarity
    def __init__(self, img_path, tags):
        self.img_path = img_path
        # Ensures tags is always a string for display purposes in the template
        self.tags = tags if isinstance(tags, str) else ", ".join(tags)

    def __str__(self):
        # Fixed the __str__ method
        return f"{self.img_path}: {self.tags}" 


# --- FLASK ROUTES ---

@app.route("/")
def index():
    """Renders the homepage."""
    return render_template("src/homepage.html")

@app.route("/wardrobe", methods=['GET', 'POST'])
def wardrobe():
    current_imgs = []

    # --- POST request logic: Handle file upload, save locally, and insert into DB ---
    if request.method == "POST":
        if collection is None:
            # Return JSON error response expected by the frontend fetch call
            return jsonify({"error": "Database connection not established."}), 500

        # 1. Get ALL files sent under the 'clothing_file' key (for multiple uploads)
        uploaded_files = request.files.getlist('clothing_file')

        if not uploaded_files:
            return jsonify({"error": "No files received for upload."}), 400

        items_to_insert = []
        
        for i, file in enumerate(uploaded_files):
            # 2. Get the corresponding tag using the index (e.g., tag_0, tag_1)
            tag_key = f'tag_{i}'
            tag = request.form.get(tag_key, 'No Tag')
            
            # 3. Secure filename and define the full local path
            filename = secure_filename(file.filename)
            file_path_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                # 4. Save the file to the desktop folder
                file.save(file_path_on_server) 

                # NOTE: If you integrate main.generate_tags, place the call here:
                # tags_from_ai = main.generate_tags(file_path_on_server)
                # tag = f"{tag}, {tags_from_ai}" 
                
                # 5. Prepare data for MongoDB (No timestamp included)
                item_data = {
                    "tag": tag,
                    "local_file_path": file_path_on_server, # Store the full path
                    "filename": filename
                }
                items_to_insert.append(item_data)
                
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                return jsonify({"error": f"Failed to save file {filename} locally."}), 500
        
        # 6. Insert all items into MongoDB Atlas
        if items_to_insert:
            try:
                collection.insert_many(items_to_insert)
                return jsonify({"message": f"Uploaded {len(items_to_insert)} items."}), 200
            except Exception as e:
                print(f"Error inserting into MongoDB: {e}")
                return jsonify({"error": "Files saved locally but failed to update database."}), 500

    # --- GET request logic: Displaying the Wardrobe from the DB ---
    
    if collection is not None:
        try:
            # Fetch all items from the database
            for item in collection.find(): 
                # Create clothingPiece object using the data fetched from the DB
                current_imgs.append(clothingPiece(item.get('local_file_path', 'No Path'), item.get('tag', 'No Tag')))
        except Exception as e:
            print(f"Error fetching data from MongoDB: {e}")
            
    # Render the template, passing the list of items
    return render_template("src/wardrobe.html", imgs=current_imgs)


if __name__ == "__main__":
    # Ensure you have run: pip install Flask pymongo werkzeug
    app.run(debug=True)