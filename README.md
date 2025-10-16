# AC & Appliance Service Booking System

A **Flask-based web application** for managing **AC, fridge, and washing machine service bookings**, allowing customers to book services and admins to manage bookings.

---

## Features

### Customer Features:
- Register and login as a customer.
- Book services like AC repair, installation, maintenance, etc.
- Track the status of bookings (Pending, In Progress, Completed).
- View previous bookings.
- Redirect to Google Maps for tracking service address.

### Admin Features:
- Admin registration and login.
- View total customers and bookings.
- Manage bookings (update status of bookings).
- View recent and completed bookings.
- Track addresses using Google Maps.

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** MySQL
- **Authentication:** Password hashing with `Werkzeug`
- **Frontend:** HTML, CSS (via Flask `render_template`)
- **Others:** URL redirection for maps, session management, flash messages.

---

## Setup Instructions

### Prerequisites:
- Python 3.x
- MySQL Server
- `pip` (Python package manager)

### 1. Install required packages
```bash
pip install flask mysql-connector-python werkzeug
```

### 2. Create MySQL Database
Create a database named ac_tech in your MySQL server:
```bash
CREATE DATABASE ac_tech;
```

### 3. Update Database Credentials
Edit the db_connector() function in app.py if needed:
```bash
def db_connector():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Add your MySQL password if any
        database="ac_tech"
    )
```
### 4. Run the Application
```bash
python app.py
```

Open your browser and go to http://127.0.0.1:5000.

## Default Admin Account

- The app automatically creates a default admin:
```
Email: admin@gmail.com
Password: admin
```
- can change this in the create_admin_if_not_exists() function.

### Folder Structure
```
├── app.py                  # Main Flask application
├── templates/              # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── admin_register.html
│   ├── home.html
│   ├── admin_dashboard.html
│   ├── booking.html
│   ├── track.html
│   ├── manage_bookings.html
│   ├── completed_bookings.html
│   └── registered_customers.html
└── README.md               # Project documentation
```

## Security

- Passwords are hashed using werkzeug.security.generate_password_hash.
- Sessions are used for both customer and admin authentication.
- Ensure to change the app.secret_key before deploying in production.

