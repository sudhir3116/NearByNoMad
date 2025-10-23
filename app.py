from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import random
import math
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.secret_key = 'nearby_nomad_secret_key_2024'

# In-memory storage
users = {}
otp_storage = {}

# Email configuration
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

# Load destinations data
def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)

# OTP generation
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via email
def send_otp(email, otp):
    otp_storage[email] = {
        'otp': otp,
        'expires': datetime.now() + timedelta(minutes=5)
    }

    print(f"📧 OTP for {email}: {otp}", flush=True)

    if SMTP_EMAIL and SMTP_PASSWORD:
        try:
            print(f"🔄 Attempting to send email to {email}...", flush=True)
            msg = MIMEMultipart()
            msg['From'] = SMTP_EMAIL
            msg['To'] = email
            msg['Subject'] = 'NearbyNomad - Your OTP Code'

            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 30px; border-radius: 8px;">
                        <h2 style="color: #FF6B35;">NearbyNomad</h2>
                        <p style="font-size: 16px; color: #333;">Your OTP code is:</p>
                        <div style="background: #fff; padding: 20px; border-radius: 6px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #FF6B35; font-size: 36px; margin: 0;">{otp}</h1>
                        </div>
                        <p style="font-size: 14px; color: #666;">This OTP will expire in 5 minutes.</p>
                        <p style="font-size: 14px; color: #666;">If you didn't request this OTP, please ignore this email.</p>
                    </div>
                </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            print(f"📡 Connecting to Gmail SMTP server...", flush=True)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.set_debuglevel(0)
            server.starttls()
            print(f"🔐 Logging in as {SMTP_EMAIL}...", flush=True)
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            print(f"📤 Sending email...", flush=True)
            server.send_message(msg)
            server.quit()

            print(f"✅ OTP email sent successfully to {email}!", flush=True)
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Gmail authentication failed: {e}", flush=True)
            print(f"💡 Check if 2-Step Verification is enabled and you're using an App Password", flush=True)
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}", flush=True)
        except Exception as e:
            print(f"❌ Failed to send email: {type(e).__name__}: {e}", flush=True)
    else:
        print(f"⚠️  Email not configured. Check SMTP_EMAIL and SMTP_PASSWORD in .env", flush=True)

# Calculate distance using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Filter destinations based on preferences
def get_recommendations(user_lat, user_lon, mood, budget, energy, place_type, subtype=None):
    destinations = load_data()
    scored_places = []

    for place in destinations:
        score = 0
        distance = calculate_distance(user_lat, user_lon, place['lat'], place['long'])

        if energy == 10 and distance > 10:
            continue
        elif energy == 50 and distance > 50:
            continue
        elif energy == 150 and distance > 150:
            continue

        if place['budget_min'] > budget:
            continue
        if place_type not in place['type']:
            continue
        if subtype and place_type == 'Eat':
            place_subtypes = place.get('subtype', [])
            if place_subtypes and subtype not in place_subtypes:
                continue

        if mood in place['mood']:
            score += 30
        score += place['rating'] * 10

        if distance < 5:
            score += 25
        elif distance < 15:
            score += 20
        elif distance < 30:
            score += 15
        elif distance < 50:
            score += 10
        else:
            score += 5

        budget_ratio = place['budget_max'] / budget if budget > 0 else 0
        if budget_ratio < 0.3:
            score += 15
        elif budget_ratio < 0.6:
            score += 10
        elif budget_ratio < 0.9:
            score += 5

        if place['status'] == 'open':
            score += 10

        place['calculated_distance'] = round(distance, 2)
        place['score'] = score
        scored_places.append(place)

    scored_places.sort(key=lambda x: (-x['score'], x['calculated_distance']))
    return scored_places[:10]

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('preferences'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email in users and users[email]['password'] == password:
            session['user'] = email
            if 'xp' not in users[email]:
                users[email]['xp'] = 0
                users[email]['level'] = 1
                users[email]['trips'] = 0
            return redirect(url_for('preferences'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        step = request.form.get('step', '1')
        if step == '1':
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            if email in users:
                return render_template('signup.html', error='Email already exists', step=1)
            otp = generate_otp()
            send_otp(email, otp)
            return render_template('signup.html', step=2, email=email, password=password, name=name)
        elif step == '2':
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            otp = request.form.get('otp')
            if email in otp_storage and otp_storage[email]['otp'] == otp:
                if datetime.now() < otp_storage[email]['expires']:
                    users[email] = {'password': password, 'name': name, 'xp': 0, 'level': 1, 'trips': 0}
                    del otp_storage[email]
                    session['user'] = email
                    return redirect(url_for('preferences'))
                else:
                    return render_template('signup.html', error='OTP expired', step=1)
            else:
                return render_template('signup.html', error='Invalid OTP', step=2, email=email, password=password, name=name)
    return render_template('signup.html', step=1)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        step = request.form.get('step', '1')
        if step == '1':
            email = request.form.get('email')
            if email not in users:
                return render_template('forgot_password.html', error='Email not found', step=1)
            otp = generate_otp()
            send_otp(email, otp)
            return render_template('forgot_password.html', step=2, email=email)
        elif step == '2':
            email = request.form.get('email')
            otp = request.form.get('otp')
            new_password = request.form.get('new_password')
            if email in otp_storage and otp_storage[email]['otp'] == otp:
                if datetime.now() < otp_storage[email]['expires']:
                    users[email]['password'] = new_password
                    del otp_storage[email]
                    return redirect(url_for('login'))
                else:
                    return render_template('forgot_password.html', error='OTP expired', step=1)
            else:
                return render_template('forgot_password.html', error='Invalid OTP', step=2, email=email)
    return render_template('forgot_password.html', step=1)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    user_email = session.get('user')
    user = users.get(user_email) if user_email else None
    if not user:
        session.pop('user', None)
        return redirect(url_for('login'))
    if request.method == 'POST':
        session['preferences'] = {
            'mood': request.form.get('mood'),
            'budget': int(request.form.get('budget')),
            'energy': int(request.form.get('energy')),
            'type': request.form.getlist('type'),
            'subtype': request.form.getlist('subtype')
        }
        return redirect(url_for('location'))
    return render_template('preferences.html', user=user)

@app.route('/location', methods=['GET', 'POST'])
def location():
    if 'user' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        session['location'] = {'lat': data['lat'], 'lon': data['lon']}
        print(f"📍 Location received: Lat={data['lat']}, Lon={data['lon']}", flush=True)
        return jsonify({'success': True})
    return render_template('location.html')

@app.route('/recommendations')
def recommendations():
    if 'user' not in session or 'preferences' not in session or 'location' not in session:
        return redirect(url_for('preferences'))

    prefs = session['preferences']
    loc = session['location']
    results = []
    for place_type in prefs['type']:
        if prefs['subtype']:
            for subtype in prefs['subtype']:
                results.extend(get_recommendations(
                    loc['lat'], loc['lon'], prefs['mood'], prefs['budget'],
                    prefs['energy'], place_type, subtype
                ))
        else:
            results.extend(get_recommendations(
                loc['lat'], loc['lon'], prefs['mood'], prefs['budget'],
                prefs['energy'], place_type
            ))

    seen = set()
    unique_results = []
    for place in results:
        if place['place_name'] not in seen:
            seen.add(place['place_name'])
            unique_results.append(place)

    unique_results.sort(key=lambda x: (-x['rating'], x['calculated_distance']))

    # Uber integration
    for place in unique_results:
        lat, lon = place['lat'], place['long']
        if 10.5 < lat < 11.5 and 76.6 < lon < 77.1:
            place['uber_available'] = True
            place['uber_link'] = f"https://m.uber.com/ul/?action=setPickup&dropoff[latitude]={lat}&dropoff[longitude]={lon}"
        else:
            place['uber_available'] = False
            place['uber_link'] = None

    users[session['user']]['trips'] += 1
    users[session['user']]['xp'] += 50
    users[session['user']]['level'] = 1 + (users[session['user']]['xp'] // 100)

    return render_template('recommendations.html', places=unique_results[:10])

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_data = users[session['user']]
    return render_template('profile.html', user=user_data, email=session['user'])

if __name__ == '__main__':
    app.run(debug=True)
