# NearbyNomad

A nearby trip planner and destination recommender built with Flask. Discover amazing places based on your mood, budget, and energy level!

## Features

- **Authentication System**: Login, Signup with OTP verification, Forgot password
- **Real Email OTP**: Gmail SMTP integration for sending OTP codes
- **Smart Recommendations**: Places filtered by mood, budget, energy level, and preferences
- **Location-Based**: Uses browser geolocation to find nearby destinations
- **Profile & Gamification**: XP system, levels, achievements, and trip tracking
- **Beautiful UI**: Clean orange/white/black aesthetic, fully responsive

## Setup

### 1. Install Dependencies

```bash
./setup.sh
```

This will create a virtual environment and install Flask and python-dotenv.

### 2. Configure Email (Optional)

For real OTP emails, create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gmail credentials:

```
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**How to get Gmail App Password:**
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Go to Security > App passwords
4. Generate app password for "Mail"
5. Copy the 16-character password

**Note:** If you don't configure email, OTP will be printed in the console.

### 3. Run the Application

```bash
./run.sh
```

Or manually:

```bash
source venv/bin/activate
python app.py
```

Visit **http://127.0.0.1:5000**

## Data

The app includes 30 real places around Coimbatore region:
- Sirumugai
- Mettupalayam
- Sathy
- Gobichettipalayam
- Erode
- And surrounding areas

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Vanilla)
- **Storage**: In-memory (dictionaries)
- **Email**: Gmail SMTP
- **Geolocation**: Browser Geolocation API

## Colors

- Primary Orange: #FF6B35
- Dark Orange: #E55A2B
- Black: #1A1A1A
- White: #FFFFFF
- Light Orange: #FFE5DC

## Project Structure

```
nearby_nomad/
├── app.py              # Main Flask application
├── data.json           # Places database (30 locations)
├── setup.sh            # Setup script
├── run.sh              # Run script
├── .env.example        # Email config template
├── static/
│   └── css/
│       └── style.css   # Styling
└── templates/          # HTML templates
    ├── base.html
    ├── login.html
    ├── signup.html
    ├── forgot_password.html
    ├── preferences.html
    ├── location.html
    ├── recommendations.html
    └── profile.html
```

## License

MIT
