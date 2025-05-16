# CITS3403-Project
# Meter - Household Utility Tracking System

![Meter Dashboard Preview](static/images/demo-screenshot.png)

## Table of Contents
- [Application Purpose](#application-purpose)
- [Group Members](#group-members)
- [Installation & Launch](#installation--launch)
- [Testing](#testing)
- [License](#license)

## Application Purpose
Meter is a Flask-based web application designed to help households track and analyze utility consumption (electricity, water, gas, WiFi). Key features of it include:

- **Visual Analytics**: Interactive charts showing consumption patterns
- **Multi-User Support**: Family member management with access control
- **Secure Authentication**: Traditional email/password login (with a solid pathway for Google OAuth login integration that only requires HTTPS to be added on in order to work)
- **Bill Sharing**: Household members can send bills to others who also use the app and are in their Family section
- **Historical Tracking**: Comparison of past utility costs

Design Specs:  
Built with Flask for backend logic, SQLAlchemy for database management, and Chart.js for data visualization. Uses a responsive design for mobile/desktop access.

## Group Members

| UWA ID      | Name             | GitHub Username       |
|-------------|------------------|-----------------------|
| 24217543    | Sacha Poulet     | @SachaPoulet          |
| 23836894    | Rishon Jose      | @rishonjose           |
| 24338952    | Justin Ho        | @JustinlikesNuggets   |
| 23962355    | James Felstead   | @James-Felstead       |

## Installation & Launch

### Prerequisites
- Python 3.8+
- pip package manager
- Google OAuth credentials (optional but still recommended to not crash the app)

### Step-by-Step Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/rishonjose/CITS3403-Project.git
   cd CITS3403-Project

2. # Activate environment:
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows

3. # Install Dependencies
pip install -r requirements.txt

4. # Create Your Own .env File
Follow the instructions set out in .env.example to set up your own SECRET_KEY, aswell as GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET

5. # Initialise The Database
flask db init
flask db migrate
flask db upgrade

6. # Run The App
export FLASK_APP=run.py  # Linux/MacOS
set FLASK_APP=run.py     # Windows
flask run
Then access the application by going to your preferred web browser, and type in http://localhost:5000 or http://127.0.0.1:5000/

## Testing

# Install testing requirements
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_authentication.py -v

## License
Made under the MIT License