from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here' # Change this to a random string in production

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Operator Model
class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if 'operator' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_operator = Operator(username=username, password=hashed_pw)
        
        try:
            db.session.add(new_operator)
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            flash("Username already exists.", "danger")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        operator = Operator.query.filter_by(username=username).first()
        if operator and check_password_hash(operator.password, password):
            session['operator'] = operator.username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'operator' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    total = None
    prev = None
    curr = None
    
    if request.method == 'POST':
        try:
            prev = float(request.form['previous_reading'])
            curr = float(request.form['current_reading'])
            
            if curr < prev:
                flash("Current reading cannot be less than previous reading.", "warning")
            else:
                total = curr - prev
        except ValueError:
            flash("Please enter valid numeric readings.", "danger")

    return render_template('dashboard.html', total=total, prev=prev, curr=curr)

@app.route('/logout')
def logout():
    session.pop('operator', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)