from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, LoginManager, login_required
from flask_mail import Mail, Message
from config import Config
from extensions import db  # Import db from extensions
from models import User  # Ensure this import is correct

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'
mail = Mail(app)

db.init_app(app)  # Initialize db with app

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(func):
    @login_required
    def decorated_view(*args, **kwargs):
        if not (current_user.is_authenticated and current_user.is_admin):
            flash("Admin access required.", "error")
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    decorated_view.__name__ = func.__name__
    return decorated_view

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email.
'''
    mail.send(msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    error_message = None

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            error_message = "Passwords do not match."
        elif User.query.filter_by(username=username).first():
            error_message = "Username already taken."
        elif User.query.filter_by(email=email).first():
            error_message = "Email already taken."
        else:
            user = User(full_name=full_name, username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
    
    return render_template('register.html', error_message=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    error_message = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            error_message = "Invalid username or password."
        else:
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
    
    return render_template('login.html', error_message=error_message)

@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/portfolio')
@login_required
def portfolio():
    return render_template('portfolio.html')

@app.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    return render_template('trade.html')

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    error_message = None
    if request.method == 'POST':
        amount = request.form.get('amount')
        flash("Deposit successful!", "success")
        return redirect(url_for('portfolio'))
    return render_template('deposit.html', error_message=error_message)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    error_message = None
    if request.method == 'POST':
        amount = request.form.get('amount')
        flash("Withdrawal successful!", "success")
        return redirect(url_for('portfolio'))
    return render_template('withdraw.html', error_message=error_message)

@app.route('/order_history')
@login_required
def order_history():
    orders = []
    return render_template('order_history.html', orders=orders)

@app.route('/create_stock', methods=['GET', 'POST'])
@admin_required
def create_stock():
    error_message = None
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        stock_name = request.form.get('stock_name')
        price = request.form.get('price')
        flash("Stock created successfully!", "success")
        return redirect(url_for('market_config'))
    return render_template('create_stock.html', error_message=error_message)

@app.route('/market_config', methods=['GET', 'POST'])
@admin_required
def market_config():
    error_message = None
    if request.method == 'POST':
        flash("Market configuration updated!", "success")
        return redirect(url_for('market_config'))
    return render_template('market_config.html', error_message=error_message)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    error_message = None
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_email(user)
            flash("An email with instructions to reset your password has been sent.", "info")
            return redirect(url_for('login'))
        else:
            error_message = "No account with that email was found."
    return render_template('reset_request.html', error_message=error_message)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for('reset_request'))
    error_message = None
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            error_message = "Passwords do not match."
        else:
            user.set_password(password)
            db.session.commit()
            flash("Your password has been updated!", "success")
            return redirect(url_for('login'))
    return render_template('reset_token.html', error_message=error_message)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
