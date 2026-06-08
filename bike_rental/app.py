from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
from dotenv import load_dotenv
import os
import hashlib

# 强制绑定静态文件目录，彻底解决图片不加载问题
load_dotenv()
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = "bike_rental_secure_premium_2026"

# 机车数据（完整保留）
bikes = [
    {
        "name": "BMW S1000RR Superbike",
        "price": "800",
        "currency": "¥",
        "image": "bmw.jpg",
        "type": "Sports Bike",
        "cc": "999cc",
        "horsepower": "205 HP",
        "weight": "197 KG",
        "mileage": "17 KM/L"
    },
    {
        "name": "Suzuki GSX-R 1000",
        "price": "700",
        "currency": "¥",
        "image": "suzuki.jpg",
        "type": "Sports Bike",
        "cc": "999cc",
        "horsepower": "199 HP",
        "weight": "203 KG",
        "mileage": "16.5 KM/L"
    },
    {
        "name": "Yamaha R15 V4 Premium",
        "price": "450",
        "currency": "¥",
        "image": "yamaha.jpg",
        "type": "Sports Bike",
        "cc": "155cc",
        "horsepower": "18.4 HP",
        "weight": "142 KG",
        "mileage": "45 KM/L"
    },
    {
        "name": "Bajaj Pulsar NS200",
        "price": "280",
        "currency": "¥",
        "image": "bajaj.jpg",
        "type": "Commuter Sports",
        "cc": "199.5cc",
        "horsepower": "24.5 HP",
        "weight": "154 KG",
        "mileage": "40 KM/L"
    },
    {
        "name": "CFMOTO 450SR",
        "price": "550",
        "currency": "¥",
        "image": "cfmoto.jpg",
        "type": "Sports Bike",
        "cc": "449cc",
        "horsepower": "50.3 HP",
        "weight": "168 KG",
        "mileage": "32 KM/L"
    },
    {
        "name": "Suzuki Hayabusa GSX1300R",
        "price": "950",
        "currency": "¥",
        "image": "hayabusa.jpg",
        "type": "Hyper Sports Bike",
        "cc": "1340cc",
        "horsepower": "190 HP",
        "weight": "266 KG",
        "mileage": "14 KM/L"
    }
]

users = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 首页路由 + 搜索筛选功能
@app.route('/')
def home():
    search_query = request.args.get('search', '').lower()
    filtered_bikes = bikes
    # 关键字模糊搜索（匹配名称、车型）
    if search_query:
        filtered_bikes = [
            bike for bike in bikes
            if search_query in bike['name'].lower() or search_query in bike['type'].lower()
        ]
    return render_template('index.html', bikes=filtered_bikes, search_query=search_query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# AI聊天接口（修复报错）
@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get("message", "")
    if not user_msg:
        return jsonify({"reply": "Please enter your question."})

    system_prompt = "You are Venom AI, a professional assistant for Biker House Motorcycle Rental. Answer clearly, cool and politely."

    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        res = requests.post(os.getenv('DEEPSEEK_API_URL'), headers=headers, json=payload, timeout=10)
        data = res.json()
        return jsonify({"reply": data["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"reply": "Venom AI service unavailable right now."})

# 登录注册路由
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        uname = request.form['username']
        email = request.form['email']
        pwd = request.form['password']
        cpwd = request.form['confirm_password']
        if uname in users:
            flash("Username already exists!")
            return redirect(url_for("register"))
        if pwd != cpwd:
            flash("Passwords do not match!")
            return redirect(url_for("register"))
        users[uname] = {"email":email, "password":hash_password(pwd)}
        flash("Registration successful! You can log in now.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        uname = request.form['username']
        pwd = hash_password(request.form['password'])
        if uname in users and users[uname]['password'] == pwd:
            session['username'] = uname
            flash("Login successful!")
            return redirect(url_for("home"))
        flash("Invalid login details!")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
