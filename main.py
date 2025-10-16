from flask import Flask, render_template, request, redirect, url_for, session,flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import webbrowser
import urllib.parse


def db_connector():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ac_tech"
    )

def create_table_if_not_exists():
    conn = db_connector()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_booking_details (
        booking_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NOT NULL,
        full_name VARCHAR(150) NOT NULL,
        phone VARCHAR(15) NOT NULL,
        address TEXT NOT NULL,
        service_type ENUM(
            'ac-repair', 'ac-installation', 'ac-maintenance', 'ac-gas-filling', 'ac-amc',
            'fridge-repair', 'fridge-maintenance', 'fridge-gas-filling',
            'washing-machine-repair', 'washing-machine-maintenance', 'washing-machine-service'
        ) NOT NULL,
        preferred_date DATE NOT NULL,
        additional_notes TEXT,
        status VARCHAR(15),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES registered_customers(id)
    )
""")
    conn.commit()
    conn.close()

def create_admin_if_not_exists():
    conn = db_connector()
    cursor = conn.cursor()

    # Create admin table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registered_admins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fname VARCHAR(100) NOT NULL,
        lname VARCHAR(100) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Insert default admin if not exists
    from werkzeug.security import generate_password_hash
    default_password = generate_password_hash("admin")  # Change password if you want
    cursor.execute("""
    INSERT IGNORE INTO registered_admins (fname, lname, email, password)
    VALUES ('suhel', 'shah', 'admin@gmail.com', %s);
    """, (default_password,))

    conn.commit()
    conn.close()


app = Flask(__name__)
app.secret_key = "mykey123"

# Ensure default admin exists
create_admin_if_not_exists()


@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        if role == "customer":
            try:
                conn = db_connector()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM registered_customers WHERE email=%s", (email,))
                user = cursor.fetchone()

                if user:
                    hashed_password = user['password']
                    if check_password_hash(hashed_password, password):
                        session['user_id'] = user['id']
                        session['user'] = f"{user['fname']} {user['lname']}"
                        return redirect(url_for('home'))
                    else:
                        message = "Invalid Credentials!"
            except Exception as e:
                print(f"error:{e}")

        elif role == "admin":
            try:
                conn = db_connector()
                cursor = conn.cursor(dictionary=True)

                # Ensure admins table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS registered_admins (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        fname VARCHAR(100) NOT NULL,
                        lname VARCHAR(100) NOT NULL,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        phone VARCHAR(15),
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("SELECT * FROM registered_admins WHERE email=%s", (email,))
                user = cursor.fetchone()

                if user:
                    hashed_password = user['password']
                    if check_password_hash(hashed_password, password):
                        session['admin_id'] = user['id']
                        session['admin'] = f"{user['fname']} {user['lname']}"
                        return redirect(url_for('admin_dashboard'))
                    else:
                        message = "Invalid Credentials!"
            except Exception as e:
                print(f"error:{e}")

    return render_template("login.html", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            message = "Passwords didn't match!"
            return render_template("register.html", message=message)

        try:
            hashed_password = generate_password_hash(password)
            conn = db_connector()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registered_customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fname VARCHAR(100) NOT NULL,
                    lname VARCHAR(100) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    phone VARCHAR(15),
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute(
                "INSERT INTO registered_customers (fname,lname,email,phone,password) VALUES (%s,%s,%s,%s,%s)",
                (fname, lname, email, phone, hashed_password)
            )
            conn.commit()

            session['user_id'] = cursor.lastrowid
            session['user'] = f"{fname} {lname}"

            conn.close()
            return redirect(url_for('home'))

        except Exception as e:
            message = f"Something wrong happened!"

    return render_template("register.html", message=message)


@app.route("/admin_register", methods=["GET", "POST"])
def admin_register():
    message = ""
    if request.method == "POST":
        fname = request.form["fname"]
        lname = request.form["lname"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            message = "Passwords didn't match!"
            return render_template("admin_register.html", message=message)

        try:
            hashed_password = generate_password_hash(password)
            conn = db_connector()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registered_admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fname VARCHAR(100) NOT NULL,
                    lname VARCHAR(100) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute(
                "INSERT INTO registered_admins (fname,lname,email,password) VALUES (%s,%s,%s,%s,%s)",
                (fname, lname, email,hashed_password)
            )
            conn.commit()

            session['admin_id'] = cursor.lastrowid
            session['admin'] = f"{fname} {lname}"

            conn.close()
            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            message = f"Something wrong happened!"

    return render_template("admin_register.html", message=message)

@app.route("/address_track")
def address_track():
    # Get the address from the query parameter
    address = request.args.get('address')
    if address:
        encoded_address = urllib.parse.quote(address)
        maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
        return redirect(maps_url)  # <- sends the user to Google Maps
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = db_connector()
        cursor = conn.cursor(dictionary=True)

        # Total customers
        cursor.execute("SELECT COUNT(*) AS total_customers FROM registered_customers")
        total_customers = cursor.fetchone()["total_customers"]

        # Total bookings
        cursor.execute("SELECT COUNT(*) AS total_bookings FROM customer_booking_details")
        total_bookings = cursor.fetchone()["total_bookings"]

        cursor.execute("SELECT COUNT(*) AS pending FROM customer_booking_details")
        pending_bookings = cursor.fetchone()["pending"]

        cursor.execute("""
            SELECT b.booking_id, b.full_name, b.service_type, b.preferred_date,b.status 
            FROM customer_booking_details b 
            ORDER BY b.created_at DESC 
            LIMIT 5
        """)
        recent_bookings = cursor.fetchall()

        conn.close()

        return render_template(
            "admin_dashboard.html",
            total_customers=total_customers,
            total_bookings=total_bookings,
            pending_bookings=pending_bookings,
            recent_bookings=recent_bookings
        )
    except Exception as e:
        print(f"error:{e}")
        return render_template("admin_dashboard.html", error=str(e))
    
@app.route("/home")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("home.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = db_connector()
        cursor = conn.cursor(dictionary=True)

        # Total customers
        cursor.execute("SELECT COUNT(*) AS total_customers FROM registered_customers")
        total_customers = cursor.fetchone()["total_customers"]

        # Total bookings
        cursor.execute("SELECT COUNT(*) AS total_bookings FROM customer_booking_details")
        total_bookings = cursor.fetchone()["total_bookings"]

        cursor.execute("SELECT COUNT(*) AS pending FROM customer_booking_details")
        pending_bookings = cursor.fetchone()["pending"]

        cursor.execute("""
            SELECT b.booking_id, b.full_name, b.service_type, b.preferred_date,b.status 
            FROM customer_booking_details b 
            ORDER BY b.created_at DESC 
            LIMIT 5
        """)
        recent_bookings = cursor.fetchall()

        conn.close()

        return render_template(
            "admin_dashboard.html",
            total_customers=total_customers,
            total_bookings=total_bookings,
            pending_bookings=pending_bookings,
            recent_bookings=recent_bookings
        )
    except Exception as e:
        print(f"error:{e}")
        return render_template("admin_dashboard.html", error=str(e))
    
@app.route("/manage_booking",methods=["GET","POST"])
def manage_booking():
    message=""
    if request.method=="POST":
        pass
    try:
        conn=db_connector()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customer_booking_details WHERE status='Pending' or status='In Progress' ORDER BY STR_TO_DATE(preferred_date, '%Y-%m-%d') DESC")
        users=cursor.fetchall()
    
        conn.close()
        return render_template("manage_bookings.html",users=users)
    except Exception as e:
        message = f"Something wrong happened!"
        return render_template("manage_bookings.html", message=message)

@app.route('/update_status/<int:booking_id>', methods=['POST'])
def update_status(booking_id):
    status = request.form.get('status')

    conn = db_connector()
    cursor = conn.cursor()
    cursor.execute("UPDATE customer_booking_details SET status = %s WHERE booking_id = %s", (status, booking_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Booking status updated successfully!", "success")
    return redirect(url_for('manage_booking'))

@app.route("/registered_customers")
def registered_customers():
    conn=db_connector()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM registered_customers")
    customers=cursor.fetchall()
    
    conn.close()
    return render_template("registered_customers.html",customers=customers)    

@app.route("/completed_bookings")
def completed_bookings():
    conn=db_connector()
    cursor=conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customer_booking_details WHERE status='Completed' ORDER BY STR_TO_DATE(preferred_date, '%Y-%m-%d') DESC")
    customers=cursor.fetchall()
    
    conn.close()
    return render_template("completed_bookings.html",customers=customers) 

@app.route("/booking", methods=["GET", "POST"])
def booking():
    message = ""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    customer_id = session['user_id']

    if request.method == "POST":
        full_name = request.form["full_name"]
        phone = request.form["phone"]
        address = request.form["address"]
        service_type = request.form["service_type"]
        preferred_date = request.form["preferred_date"]
        additional_notes = request.form["additional_notes"]

        try:
            create_table_if_not_exists()
            conn = db_connector()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO customer_booking_details 
                (customer_id, full_name, phone, address, service_type, preferred_date, additional_notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (customer_id, full_name, phone, address, service_type, preferred_date, additional_notes, 'Pending'))


            conn.commit()
            conn.close()
            return redirect(url_for("home"))
        except Exception as e:
            print(f"Error: {e}")
            message = "Something went wrong. Please try again."
            return render_template("booking.html", message=message, minimal_nav=True)

    return render_template("booking.html", message=message, minimal_nav=True)
@app.route("/track")
def track():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        conn = db_connector()
        cursor = conn.cursor(dictionary=True)

        # Fetch all bookings for this logged-in user
        cursor.execute("""
            SELECT * FROM customer_booking_details
            WHERE customer_id = %s
            ORDER BY STR_TO_DATE(preferred_date, '%%Y-%%m-%%d') DESC
        """, (user_id,))
        bookings = cursor.fetchall()
        conn.close()

        return render_template("track.html", bookings=bookings, minimal_nav=True)
    
    except Exception as e:
        return render_template("track.html", message=f"Something went wrong: {e}", minimal_nav=True)
@app.route("/logout")
def logout():
    # Clear both customer and admin sessions
    session.clear()
    flash("You have been logged out successfully!", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
