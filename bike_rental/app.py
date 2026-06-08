try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random
import requests
import os

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "bikehouse_secure_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bikehouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    cc = db.Column(db.Integer, nullable=False)
    hp = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Float, nullable=False)
    is_premium = db.Column(db.Boolean, default=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Load DeepSeek API Keys from Render Environment Variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

def dogesh_ai(user_prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are Dogesh AI, professional motorcycle consultant for Bike House rental. Answer questions simply and friendly."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    try:
        res = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=15)
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return "AI service unavailable right now, please try again later."

# Routes
@app.route('/')
def home():
    premium_bikes = Bike.query.filter_by(is_premium=True).limit(2).all()
    return render_template('index.html', bikes=premium_bikes)

@app.route('/all-bikes')
def all_bikes():
    return render_template('all-bikes.html', bikes=Bike.query.all())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"], password=request.form["password"]).first()
        if user:
            session["user"] = user.email
            return redirect('/')
        flash("Wrong email or password")
    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if User.query.filter_by(email=request.form["email"]).first():
            flash("Email already registered")
            return redirect('/register')
        new_user = User(email=request.form["email"], password=request.form["password"])
        db.session.add(new_user)
        db.session.commit()
        flash("Register successful, please login")
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/ai-chat', methods=['POST'])
def ai_chat():
    user_msg = request.form.get("msg", "")
    reply = dogesh_ai(user_msg)
    return reply

@app.route('/init-bikes')
def init_bikes():
    db.drop_all()
    db.create_all()
    bike_list = [
        Bike(name="Yamaha R1", price=399, cc=998, hp=200, weight=199, mileage=15.5, is_premium=True),
        Bike(name="Ducati V4", price=459, cc=1103, hp=214, weight=195, mileage=14.8, is_premium=True),
        Bike(name="BMW S1000RR", price=429, cc=999, hp=205, weight=197, mileage=15.2),
        Bike(name="Kawasaki ZX10R", price=389, cc=998, hp=197, weight=200, mileage=15.0),
        Bike(name="Honda CBR1000RR", price=379, cc=999, hp=189, weight=201, mileage=16.0),
        Bike(name="Suzuki GSXR1000", price=369, cc=999, hp=199, weight=202, mileage=15.8),
        Bike(name="Aprilia RSV4", price=449, cc=1099, hp=217, weight=189, mileage=14.5),
        Bike(name="KTM RC1000", price=399, cc=1000, hp=200, weight=190, mileage=15.1),
        Bike(name="Triumph Daytona", price=385, cc=765, hp=128, weight=165, mileage=18.2),
        Bike(name="MV Agusta F4", price=489, cc=998, hp=208, weight=190, mileage=14.9),
    ]
    db.session.bulk_save_objects(bike_list)
    db.session.commit()
    return "Bike data inserted successfully!"

# Render Port Fix (Critical Line For Hosting)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
