# --- Email and Token Configuration ---
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message

# Replace with your actual credentials for an SMTP server (e.g., Gmail, SendGrid, etc.)
# Note: You may need to generate an App Password for services like Gmail.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com' # Sender email
app.config['MAIL_PASSWORD'] = 'your_app_password'     # Sender password (or app password)

mail = Mail(app)

# Serializer uses the secret key to encode and decode tokens
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # 1. Add email field
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password_hash = db.Column(db.String(128), nullable=False)
    # 2. Add verification status field
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False) 

    # ... (set_password and check_password methods remain the same)

def generate_confirmation_token(email):
    """Generates a secure token containing the user's email."""
    # The 'confirmation' salt ensures the token is only valid for confirmation links
    return serializer.dumps(email, salt='email-confirm-salt')

def send_confirmation_email(user_email):
    """Sends the email with the confirmation link."""
    token = generate_confirmation_token(user_email)
    
    # Generate the full URL for the confirmation route
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
    

    # ... (existing imports and setup)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # ... (omitted existing check for current_user.is_authenticated)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email') # Get the email from the form
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user or email_exists:
            flash('Username or email is already in use.', 'danger')
        else:
            new_user = User(username=username, email=email) # Include email
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            # --- ACTION: Send confirmation email after successful registration ---
            send_confirmation_email(email)
            
            flash('Success! A confirmation email has been sent. Please check your inbox.', 'info')
            return redirect(url_for('login'))
            
    return render_template('src/register.html')


@app.route('/confirm/<token>')
def confirm_email(token):
    """Route handles the link clicked by the user in the email."""
    try:
        # Load the email from the token. max_age is in seconds (30 minutes)
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
        login_user(user) # Optionally log the user in immediately
        flash('Email successfully confirmed! You are now logged in.', 'success')
    elif user and user.email_confirmed:
        flash('Account already confirmed. Please log in.', 'success')
    else:
        flash('Account not found.', 'danger')

    return redirect(url_for('wardrobe'))