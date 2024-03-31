from flask import Flask, render_template, redirect, request, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lacetrack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

load_dotenv()

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # For demo only, use hashed passwords in prod!
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_pic = db.Column(db.String(256), nullable=True)
    shoes = db.relationship('Shoe', backref='owner', lazy=True)

class Shoe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_bought = db.Column(db.Float, nullable=False)
    price_sold = db.Column(db.Float, default=0.0)
    date_bought = db.Column(db.String(20), nullable=False)
    date_sold = db.Column(db.String(20), default="--/--/--")
    status = db.Column(db.String(20), default="0")
    tracking_number = db.Column(db.String(120), default="")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper to get or create a default user for local testing
init_done = False

def get_default_user():
    user = User.query.filter_by(username='demo').first()
    if not user:
        user = User(username='demo', password='demo', email='demo@example.com')
        db.session.add(user)
        db.session.commit()
    return user

@app.before_request
def initialize():
    global init_done
    if not init_done:
        db.create_all()
        get_default_user()
        init_done = True

@app.route('/')
def index():
    user = get_default_user()
    return render_template('index.html', user=user)

@app.route('/portal')
def portal():
    user = get_default_user()
    page = int(request.args.get('page', 1))
    per_page = 10
    shoes_query = Shoe.query.filter_by(owner=user)
    total_shoes = shoes_query.count()
    total_pages = (total_shoes + per_page - 1) // per_page
    shoes = shoes_query.offset((page-1)*per_page).limit(per_page).all()
    stats = {
        'number_of_shoes': sum([s.quantity for s in Shoe.query.filter_by(owner=user).all()]),
        'total_sales': sum([s.price_sold * s.quantity for s in Shoe.query.filter_by(owner=user).all()]),
        'total_profit': sum([(s.price_sold - s.price_bought) * s.quantity for s in Shoe.query.filter_by(owner=user).all()]),
    }
    stats['total_sales'] = f"${stats['total_sales']:,.2f}"
    stats['total_profit'] = f"${stats['total_profit']:,.2f}"
    return render_template('portal.html', user=user, stats=stats, shoes=shoes, page=page, total_pages=total_pages)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('portal'))
        else:
            flash('Invalid credentials')
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add-shoe', methods=['POST'])
def add_shoe():
    user = get_default_user()
    name = request.form['name']
    size = request.form['size']
    quantity = int(request.form['quantity'])
    price_bought = float(request.form['price_bought'])
    date_bought = request.form['date_bought']
    shoe = Shoe(name=name, size=size, quantity=quantity, price_bought=price_bought, user_id=user.id, date_bought=date_bought)
    db.session.add(shoe)
    db.session.commit()
    return redirect(url_for('portal'))

@app.route('/update-shoe', methods=['POST'])
def update_shoe():
    user = get_default_user()
    shoe_id = int(request.form.get('shoe_id', 0))
    shoe = Shoe.query.filter_by(id=shoe_id, user_id=user.id).first()
    if shoe:
        shoe.status = request.form.get('status', shoe.status)
        shoe.date_sold = request.form.get('date_sold', shoe.date_sold)
        shoe.price_sold = float(request.form.get('price_sold', shoe.price_sold))
        shoe.tracking_number = request.form.get('tracking_number', shoe.tracking_number)
        if 'size' in request.form:
            shoe.size = request.form.get('size', shoe.size)
        db.session.commit()
    return redirect(url_for('portal'))

@app.route('/delete-shoe', methods=['POST'])
def delete_shoe():
    user = get_default_user()
    shoe_id = int(request.form.get('shoe_id', 0))
    shoe = Shoe.query.filter_by(id=shoe_id, user_id=user.id).first()
    if shoe:
        db.session.delete(shoe)
        db.session.commit()
    return redirect(url_for('portal'))

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.route('/api/sneaker-suggestions')
def sneaker_suggestions():
    q = request.args.get('q', '').strip()
    if not q:
        return {"suggestions": []}
    prompt = f"List 10 sneaker names that start with or contain: '{q}'. Only return the names, comma separated."
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a sneaker expert."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.5
    }
    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        # Split by comma, strip whitespace
        suggestions = [s.strip() for s in text.split(",") if s.strip()]
        return {"suggestions": suggestions}
    except Exception as e:
        return {"suggestions": [], "error": str(e)}

@app.route('/api/check-tracking')
def check_tracking():
    tracking_number = request.args.get('tracking_number', '').strip()
    if not tracking_number:
        return {"status": None, "carrier": None, "details": "No tracking number provided."}
    # Always ask the LLM for status, do not try to detect carrier
    try:
        prompt = f"Given the tracking number '{tracking_number}', what is the most likely status or next step? If you can't look it up, say so, but provide a likely status based on the format."
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a shipping and logistics expert."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 100,
            "temperature": 0.5
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        status = text.strip()
        details = 'LLM generated.'
    except Exception as e:
        status = None
        details = f'LLM error: {str(e)}'
    return {"status": status, "carrier": None, "details": details}

@app.route('/api/stockx-info')
def stockx_info():
    q = request.args.get('q', '').strip()
    if not q:
        return {"info": None, "source": "StockX", "details": "No query provided."}
    try:
        prompt = f"For the sneaker '{q}', provide the latest StockX price, sales volume, and a short market summary. If you can't look it up, make a realistic guess."
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a sneaker market analyst."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        info = text.strip()
        details = 'LLM generated StockX info.'
    except Exception as e:
        info = None
        details = f'LLM error: {str(e)}'
    return {"info": info, "source": "StockX", "details": details}

@app.route('/api/ebay-info')
def ebay_info():
    q = request.args.get('q', '').strip()
    if not q:
        return {"info": None, "source": "eBay", "details": "No query provided."}
    try:
        prompt = f"For the sneaker '{q}', provide the latest eBay sold price, number of recent sales, and a short market summary. If you can't look it up, make a realistic guess."
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a sneaker market analyst."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        info = text.strip()
        details = 'LLM generated eBay info.'
    except Exception as e:
        info = None
        details = f'LLM error: {str(e)}'
    return {"info": info, "source": "eBay", "details": details}

@app.route('/analytics')
def analytics():
    user = get_default_user()
    shoes = Shoe.query.filter_by(owner=user).all()
    # Filters
    period = request.args.get('period', 'all')
    status = request.args.get('status', 'all')
    # Filter shoes by status
    if status != 'all':
        shoes = [s for s in shoes if str(s.status) == status]
    # Filter by time period
    from datetime import datetime, timedelta
    now = datetime.now()
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, '%m/%d/%Y')
        except:
            return None
    if period != 'all':
        days = int(period)
        shoes = [s for s in shoes if parse_date(s.date_sold) and (now - parse_date(s.date_sold)).days <= days]
    # Profit/Loss per shoe
    profit_labels = [s.name for s in shoes]
    profit_values = [(s.price_sold - s.price_bought) * s.quantity for s in shoes]
    profit_data = {"labels": profit_labels, "datasets": [{"label": "Profit/Loss", "data": profit_values, "backgroundColor": "#4caf50"}]}
    # Sales Velocity (shoes sold per month)
    from collections import Counter
    months = [parse_date(s.date_sold).strftime('%Y-%m') for s in shoes if parse_date(s.date_sold)]
    month_counts = Counter(months)
    velocity_data = {"labels": list(month_counts.keys()), "datasets": [{"label": "Sales Velocity", "data": list(month_counts.values()), "borderColor": "#2196f3", "fill": False}]}
    # Average Hold Time (days between bought and sold)
    hold_labels = [s.name for s in shoes if parse_date(s.date_sold) and parse_date(s.date_bought)]
    hold_values = [(parse_date(s.date_sold) - parse_date(s.date_bought)).days for s in shoes if parse_date(s.date_sold) and parse_date(s.date_bought)]
    hold_data = {"labels": hold_labels, "datasets": [{"label": "Hold Time (Days)", "data": hold_values, "backgroundColor": "#ff9800"}]}
    # ROI (%)
    roi_labels = [s.name for s in shoes if s.price_bought > 0]
    roi_values = [round(100 * (s.price_sold - s.price_bought) / s.price_bought, 2) if s.price_bought > 0 else 0 for s in shoes]
    roi_data = {"labels": roi_labels, "datasets": [{"label": "ROI %", "data": roi_values, "backgroundColor": "#9c27b0"}]}
    return render_template('analytics.html', profit_data=profit_data, velocity_data=velocity_data, hold_data=hold_data, roi_data=roi_data)

@app.route('/export-csv')
def export_csv():
    user = get_default_user()
    shoes = Shoe.query.filter_by(owner=user).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Size', 'Quantity', 'Price Bought', 'Date Bought', 'Price Sold', 'Date Sold', 'Status', 'Tracking Number'])
    for s in shoes:
        writer.writerow([s.name, s.size, s.quantity, s.price_bought, s.date_bought, s.price_sold, s.date_sold, s.status, s.tracking_number])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='inventory.csv')

@app.route('/import-csv', methods=['POST'])
def import_csv():
    user = get_default_user()
    file = request.files['file']
    if not file:
        return redirect(url_for('portal'))
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)
    for row in reader:
        shoe = Shoe(name=row['Name'], size=row['Size'], quantity=int(row['Quantity']), price_bought=float(row['Price Bought']), date_bought=row['Date Bought'], price_sold=float(row['Price Sold']), date_sold=row['Date Sold'], status=row['Status'], tracking_number=row['Tracking Number'], user_id=user.id)
        db.session.add(shoe)
    db.session.commit()
    return redirect(url_for('portal'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

# Make sure your Flask app is running at http://127.0.0.1:5000
driver = webdriver.Chrome()  # or webdriver.Firefox() if you use Firefox
driver.get("http://127.0.0.1:5000")

# Now you can interact with the page using Selenium commands 