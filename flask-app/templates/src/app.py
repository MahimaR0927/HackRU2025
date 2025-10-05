import os
from flask import Flask, request, url_for, redirect, render_template, flash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
# Assuming you are using Flask-SQLAlchemy for the User model
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user # Import necessary components
from dotenv import load_dotenv # Import to load .env file
import main

# Load environment variables from .env file
load_dotenv()

# --- Setup Placeholders (Ensure these match your actual setup) ---
# NOTE: You MUST install Flask-SQLAlchemy and Flask-Login
app = Flask(__name__)
# CRITICAL FIX: Read SECRET_KEY from environment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-secret-key-change-me') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# --- Email and Token Configuration (Read from Environment Variables) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# --- THIS IS THE FIX ---
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# --- END OF FIX ---

# CRITICAL FIX 2: This reads the public URL (SERVER_NAME) from your .env file
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')

mail = Mail(app)

# Serializer uses the secret key to encode and decode tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password_hash = db.Column(db.String(128), nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False) 

    # Placeholder methods (you need to implement the actual hashing/checking)
    def set_password(self, password):
        self.password_hash = password # Needs hashing implementation
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


def generate_confirmation_token(email):
    """Generates a secure token containing the user's email."""
    return serializer.dumps(email, salt='email-confirm-salt')

def send_confirmation_email(user_email):
    """Sends the email with the confirmation link."""
    token = generate_confirmation_token(user_email)
    
    # This block ensures that url_for uses the SERVER_NAME set in app.config
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


# --- Wardrobe Routes (File Handling) ---

# Configuration for file storage
UPLOAD_FOLDER = 'templates/static/images' 
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, UPLOAD_FOLDER)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class clothingPiece:
    def __init__(self, *args):
        self.img_path = args[0]
        self.tags = args[1]


@app.route("/")
def index():
    """Renders the homepage."""
    return render_template("src/homepage.html")


@app.route("/wardrobe", methods=['GET', 'POST'])
def wardrobe():
    """Handles file upload and displays existing wardrobe items."""
    imgs = [] 
    error = ""

    try:
        if request.method == "POST":
            uploaded_files = request.files.getlist('clothing_file')
            
            if not uploaded_files:
                error = "No files selected for upload."
            
            for index, file in enumerate(uploaded_files):
                if file.filename:
                    tag_key = f'tag_{index}'
                    user_tag = request.form.get(tag_key, 'default')

                    filename = os.path.basename(file.filename)
                    file_path_on_server = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    file.save(file_path_on_server)
                    
                    print(f'File uploaded successfully: {filename} with tag: {user_tag}')
                    
                    tags = [user_tag] 
                    new_item = clothingPiece(filename, tags)
                    imgs.append(new_item)
            
        # --- Database Fetching Placeholder (GET and POST after upload) ---
        pass 
        
    except Exception as e:
        error = f"An upload or database error occurred: {e}"
        print(f"Wardrobe Route Error: {error}")
        imgs = []

    return render_template("src/wardrobe.html", imgs=imgs, upload_error=error)


# --- Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration requests."""
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
            # The 'login' route is needed for this redirect
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
        # login_user(user) # Optionally log the user in immediately
        flash('Email successfully confirmed! You are now logged in.', 'success')
    elif user and user.email_confirmed:
        flash('Account already confirmed. Please log in.', 'success')
    else:
        flash('Account not found.', 'danger')

    return redirect(url_for('index'))