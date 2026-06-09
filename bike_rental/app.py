from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.secret_key = "bikerhouse_secure_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bikehouse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False

db = SQLAlchemy(app)

# =============================
# YOUR GROQ API KEY (WORKING)
# =============================
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    cc = db.Column(db.String(100), nullable=False)
    horsepower = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.String(100), nullable=False)
    mileage = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fullname = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

@app.route('/set-lang/<lang>')
def set_language(lang):
    if lang in ['en','cn']:
        session['lang'] = lang
    return redirect(request.referrer or '/')

# --------------------------
# GROQ AI CHAT (100% FIXED)
# --------------------------
@app.route('/api/chat', methods=['POST'])
def api_chat():
    user_message = request.form.get('msg', '').strip()
    if not user_message:
        return "Please type your question."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are Jakson, Biker House motorcycle rental assistant. Be friendly, short, clear. Answer in English or Chinese. Only answer about bikes, rental, prices, booking, services."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=15)
        response_data = response.json()

        if "choices" in response_data:
            return response_data["choices"][0]["message"]["content"].strip()
        elif "error" in response_data:
            return f"AI Error: {response_data['error']['message']}"
        else:
            return "Sorry, AI is temporarily unavailable. Try again later."
    except Exception as e:
        print("Groq Error:", str(e))
        return "Cannot connect to AI. Please check internet or API key."

# -----------------------------------------------------------------------------------

@app.route('/save-booking', methods=['POST'])
def save_booking():
    fullname = request.form.get('fullname', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    days = int(request.form.get('days', 1))
    bike_name = request.form.get('bike_name', '')
    daily_price = int(request.form.get('bike_price', 0))
    total_price = daily_price * days

    booking_info = {
        'fullname': fullname,
        'phone': phone,
        'address': address,
        'days': days,
        'bike_name': bike_name,
        'daily_price': daily_price,
        'total_price': total_price
    }
    session['booking_data'] = booking_info
    return redirect(url_for('payment_page'))

@app.route('/payment')
def payment_page():
    if 'booking_data' not in session:
        return redirect('/')
    return render_template('payment.html', booking=session['booking_data'])

@app.route('/all-bikes')
def all_bikes():
    search_q = request.args.get('search','').strip()
    if search_q:
        bikes = Bike.query.filter(Bike.name.ilike(f'%{search_q}%') | Bike.type.ilike(f'%{search_q}%')).all()
    else:
        bikes = Bike.query.all()
    return render_template('all-bikes.html', bikes=bikes)

@app.route('/')
def home():
    bikes = Bike.query.limit(6).all()
    return render_template('index.html', bikes=bikes)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect('/')
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        if not email.endswith("@gmail.com"):
            return "<script>alert('Only Gmail Accounts Are Allowed!');window.location.href='/login'</script>"
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["username"] = user.email
            session["fullname"] = user.fullname
            return redirect('/')
        return "<script>alert('Wrong Email or Password!');window.location.href='/login'</script>"
    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if "username" in session:
        return redirect('/')
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        if not email.endswith("@gmail.com"):
            return "<script>alert('Only Gmail Address Allowed!');window.location.href='/register'</script>"
        if User.query.filter_by(email=email).first():
            return "<script>alert('This Gmail Already Registered!');window.location.href='/login'</script>"
        session['reg_email'] = email
        session['reg_pass'] = password
        return redirect('/fill-profile')
    return render_template('register.html')

@app.route('/fill-profile', methods=["GET","POST"])
def fill_profile():
    if 'reg_email' not in session:
        return redirect('/register')
    if request.method == "POST":
        fullname = request.form.get('fullname','').strip()
        phone = request.form.get('phone','').strip()
        email = session['reg_email']
        password = session['reg_pass']
        new_user = User(email=email,password=password,fullname=fullname,phone=phone)
        db.session.add(new_user)
        db.session.commit()
        session.pop('reg_email', None)
        session.pop('reg_pass', None)
        session["username"] = email
        session["fullname"] = fullname
        return redirect(url_for('home'))
    return render_template('fill-profile.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

def init_bikes():
    if Bike.query.count() == 0:
        bike_list = [
            {"name":"Bajaj Bike","image":"bajaj.jpg","type":"Standard","price":75,"cc":"160 CC","horsepower":"15 HP","weight":"148 KG","mileage":"42 KM/L"},
            {"name":"BMW Bike","image":"bmw.jpg","type":"Sports","price":320,"cc":"1000 CC","horsepower":"165 HP","weight":"210 KG","mileage":"18 KM/L"},
            {"name":"CFMoto Bike","image":"cfmoto.jpg","type":"Adventure","price":190,"cc":"450 CC","horsepower":"48 HP","weight":"205 KG","mileage":"25 KM/L"},
            {"name":"Hayabusa","image":"hayabusa.jpg","type":"Superbike","price":450,"cc":"1340 CC","horsepower":"197 HP","weight":"266 KG","mileage":"14 KM/L"},
            {"name":"Repsol","image":"hero-bike.jpg","type":"Commuter","price":60,"cc":"125 CC","horsepower":"11 HP","weight":"132 KG","mileage":"50 KM/L"},
            {"name":"Yamaha Bike","image":"yamaha.jpg","type":"Sports Naked","price":270,"cc":"890 CC","horsepower":"119 HP","weight":"197 KG","mileage":"20 KM/L"}
        ]
        for b in bike_list:
            db.session.add(Bike(**b))
        db.session.commit()

with app.app_context():
    db.create_all()
    init_bikes()

if __name__ == '__main__':
    app.run(debug=True)
