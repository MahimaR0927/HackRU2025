import os
import json 
from flask import Flask, request, render_template, jsonify, url_for, redirect, flash
# --- AUTH IMPORTS (NEW) ---
from flask_sqlalchemy import SQLAlchemy
# NOTE: Added 'current_user' and 'logout_user' to this import line
from flask_login import UserMixin, login_user, LoginManager, logout_user, current_user 
# --- END AUTH IMPORTS ---
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
import main

load_dotenv() # Load environment variables

# --- 1. CONFIGURATION ---
# Note: Since you are using SQLAlchemy for users and PyMongo for items, 
# I will retain the MongoDB connection section below, but these are 
# the configurations for the core Flask app and the SQLite user database.
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key-change-me') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' # Use a separate DB for users
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Required by Flask-Login to reload the user object from the user ID stored in the session."""
    return User.query.get(int(user_id))
# --- END SQLALCHEMY/FLASK-LOGIN CONFIGURATION ---

# --- Email and Token Configuration (Read from Environment Variables) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME') # For generating external URLs

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# 3. Local File Storage Path: HACKRU/flask-app/static/images
UPLOAD_FOLDER = 'templates/static/images' 
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, UPLOAD_FOLDER)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# print(f"Upload folder path: {app.config['UPLOAD_FOLDER']}") # Debugging print removed


# --- MONGODB CONNECTION (Kept in case you need it for /wardrobe) ---
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://mahimar0927:jqIIIk3sxoUMTqkV@cluster0.d0oisrw.mongodb.net/")
DB_NAME = "Outfits_db"
COLLECTION_NAME = "choices"
client = None
collection = None
try:
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI)
    db_mongo = client[DB_NAME] 
    collection = db_mongo[COLLECTION_NAME]
    client.admin.command('ping') 
    # print("Successfully connected to MongoDB Atlas.") # Debugging print removed
except Exception as e:
    # Error handling remains minimal to keep app running
    pass 
# -------------------------------------------------------------------


# --- 5. USER MODEL (UPDATED) ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password_hash = db.Column(db.String(128), nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False) 

    # TEMPORARY INSECURE PASSWORD METHODS: REPLACE LATER!
    def set_password(self, password):
        self.password_hash = password 
    
    # ADDED: Method required by the login logic
    def check_password(self, password):
        """Checks if the provided password matches the stored hash (currently plain text)."""
        return self.password_hash == password

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
# --- END USER MODEL ---


def generate_confirmation_token(email):
    """Generates a secure token containing the user's email."""
    return serializer.dumps(email, salt='email-confirm-salt')

def send_confirmation_email(user_email):
    """Sends the email with the confirmation link."""
    token = generate_confirmation_token(user_email)
    
    with app.app_context():
        confirm_url = url_for('confirm_email', token=token, _external=True)
    
    msg = Message(
        subject="Confirm Your Email Address",
        recipients=[user_email],
        body=f"Hello,\n\nPlease click the link below to confirm your email address for your account:\n\n{confirm_url}\n\nThis link will expire in 30 minutes."
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Mail send failed: {e}")
        flash('Failed to send confirmation email. Please check server logs.', 'danger')
        return False


# --- Wardrobe Data Model (Simplified for current context) ---

class clothingPiece:
    def __init__(self, *args):
        self.img_path = args[0]
        self.tags = args[1]


@app.route("/")
def index():
    """Renders the homepage."""
    return render_template("src/login.html")

@app.route("/homepage")
def index():
    """Renders the homepage."""
    return render_template("src/homepage.html")


@app.route("/outfits")
def outfits():
    """Renders the outfits page."""
    return render_template("src/outfits.html")


@app.route("/wardrobe", methods=['GET', 'POST'])
def wardrobe():
    """Handles file upload and displays existing wardrobe items."""
    imgs = [] 
    error = ""
    # Simplified wardrobe logic for context
    return render_template("src/wardrobe.html", imgs=imgs, upload_error=error)


# --- Authentication Routes (COMPLETED) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the login page and handles login form submission."""
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('wardrobe'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 1. Look up user by username
        user = User.query.filter_by(username=username).first()
        
        # 2. Check user exists, password is correct, and email is confirmed
        if user and user.check_password(password) and user.email_confirmed:
            login_user(user)
            flash(f'Logged in successfully as {user.username}.', 'success')
            
            # Redirect to the page they were trying to access, or default to wardrobe
            next_page = request.args.get('next')
            return redirect(next_page or url_for('wardrobe'))
        elif user and not user.email_confirmed:
             flash('Your email has not been confirmed. Please check your inbox.', 'warning')
        else:
            flash('Login failed. Check your username and password.', 'danger')
        
    return render_template('src/login_form.html')

@app.route('/logout')
def logout():
    """Logs the current user out."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration requests."""
    # Check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('wardrobe'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user or email_exists:
            flash('Username or email is already in use.', 'danger')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            send_confirmation_email(email)
            
            flash('Success! A confirmation email has been sent. Please check your inbox.', 'info')
            return redirect(url_for('login')) 
            
    return render_template('src/register.html')


@app.route('/confirm/<token>')
def confirm_email(token):
    """Route handles the link clicked by the user in the email."""
    try:
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=1800 
        )
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('register'))

    user = User.query.filter_by(email=email).first()
    
    if user and not user.email_confirmed:
        user.email_confirmed = True
        db.session.commit()
        flash('Email successfully confirmed! Please log in.', 'success') 
        return redirect(url_for('login')) 
    elif user and user.email_confirmed:
        flash('Account already confirmed. Please log in.', 'success')
    else:
        flash('Account not found.', 'danger')

    return redirect(url_for('index'))


if __name__ == "__main__":
    # --- Initialize SQL Alchemy DB and create tables ---
    with app.app_context():
        db.create_all()
    # --- END DB Init ---
    app.run(debug=True)
