from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # revert to 256 if desired
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        # Revert to pbkdf2 for shorter hash output
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        from utils import generate_reset_token
        return generate_reset_token(self.id, expires_sec)

    @staticmethod
    def verify_reset_token(token):
        from utils import verify_reset_token
        user_id = verify_reset_token(token)
        if user_id:
            return User.query.get(user_id)
        return None

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)
    stock_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    # ...additional fields if necessary...

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('portfolios', lazy=True))
    stock = db.relationship('Stock', backref=db.backref('portfolios', lazy=True))
    # ...additional fields if necessary...

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    order_type = db.Column(db.String(10), nullable=False)  # e.g., 'buy' or 'sell'
    shares = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    stock = db.relationship('Stock', backref=db.backref('orders', lazy=True))
    # ...additional fields if necessary...

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # e.g., 'deposit' or 'withdrawal'
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    user = db.relationship('User', backref=db.backref('transactions', lazy=True))
    # ...additional fields if necessary...
