from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, LoginManager  # Added logout_user and LoginManager import
# Ensure flask_login is configured
# Assume User model and db are imported

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If the user is already authenticated, redirect them
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    error_message = None

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Basic validations
        if password != confirm_password:
            error_message = "Passwords do not match."
        elif User.query.filter_by(username=username).first():
            error_message = "Username already taken."
        elif User.query.filter_by(email=email).first():
            error_message = "Email already taken."
        else:
            # Create and save the user
            user = User(full_name=full_name, username=username, email=email)
            user.set_password(password)  # Assume set_password hashes the password
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
        
        # Placeholder: Validate user credentials. Replace with your authentication logic.
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            error_message = "Invalid username or password."
        else:
            # Perform login, e.g., using login_user from flask_login
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
def index():
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/trade')
def trade():
    return render_template('trade.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    error_message = None
    if request.method == 'POST':
        amount = request.form.get('amount')
        # ...validate and update user's balance...
        flash("Deposit successful!", "success")
        return redirect(url_for('portfolio'))
    return render_template('deposit.html', error_message=error_message)

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    error_message = None
    if request.method == 'POST':
        amount = request.form.get('amount')
        # ...validate funds and update user's balance...
        flash("Withdrawal successful!", "success")
        return redirect(url_for('portfolio'))
    return render_template('withdraw.html', error_message=error_message)

@app.route('/order_history')
def order_history():
    # Placeholder: Retrieve order history from the database
    orders = []  # Replace with real query to fetch orders for current_user
    return render_template('order_history.html', orders=orders)

@app.route('/create_stock', methods=['GET', 'POST'])
def create_stock():
    # Ensure only admins can access this route (custom logic needed)
    if not (current_user.is_authenticated and current_user.is_admin):
        flash("Unauthorized access.", "error")
        return redirect(url_for('index'))
    
    error_message = None
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        stock_name = request.form.get('stock_name')
        price = request.form.get('price')
        # ...validate and create stock logic...
        flash("Stock created successfully!", "success")
        return redirect(url_for('market_config'))
    
    return render_template('create_stock.html', error_message=error_message)

@app.route('/market_config', methods=['GET', 'POST'])
def market_config():
    # Ensure only admins can access this route (custom logic needed)
    if not (current_user.is_authenticated and current_user.is_admin):
        flash("Unauthorized access.", "error")
        return redirect(url_for('index'))
    
    error_message = None
    if request.method == 'POST':
        # ...process market configuration settings...
        flash("Market configuration updated!", "success")
        return redirect(url_for('market_config'))
    
    return render_template('market_config.html', error_message=error_message)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    # Optionally: db.session.rollback() for database errors
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
