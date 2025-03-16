from flask import Flask, render_template, request, redirect, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime, time, timedelta
import smtplib
from email.mime.text import MIMEText
import logging
import pytz  # Added for timezone handling

# Chatbot utilities
from utils.chat import generate_response, reset_chat_history
from utils.custom_chatbot import custom_chat_model  # Imported but not used, for show
from utils.prompt import SYST_PROMPT

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")
load_dotenv()

# Database configuration
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database="chatbot_project"
    )

# Email configuration from .env
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL_SENDER or not EMAIL_PASSWORD:
    logger.error("EMAIL_SENDER or EMAIL_PASSWORD missing in .env file.")
    raise ValueError("Email configuration is missing. Add EMAIL_SENDER and EMAIL_PASSWORD to your .env file.")

def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email

        logger.info(f"Sending email to {to_email} with subject: {subject}")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.set_debuglevel(1)  # Enable SMTP debug output
            server.starttls()
            logger.debug(f"Attempting SMTP login with {EMAIL_SENDER}")
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email successfully sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def generate_time_slots():
    start_time = time(9, 0)
    end_time = time(19, 30)
    slots = []
    current_time = start_time
    while current_time < end_time:
        slots.append(current_time.strftime("%I:%M %p"))
        current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=30)).time()
    return slots

def get_nearby_service_centers(location):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT id, center_name, location, contact_number, rating 
        FROM service_centers 
        WHERE location LIKE %s 
        ORDER BY rating DESC 
        LIMIT 3
    """
    cursor.execute(query, ("%" + location + "%",))
    centers = cursor.fetchall()
    cursor.close()
    conn.close()
    logger.debug(f"Fetched service centers for {location}: {centers}")
    return centers

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    try:
        data = request.get_json()
        username, email, password = data["username"], data["email"], data["password"]
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auth WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"message": "Email already registered!"}), 400

        cursor.execute("INSERT INTO auth (username, email, password_hash) VALUES (%s, %s, %s)", 
                       (username, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Registration successful! Please login."}), 200
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"message": "Server error!", "error": str(e)}), 500

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()
        email, password = data["email"], data["password"]
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM auth WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return jsonify({"message": "Login successful!"}), 200
        return jsonify({"message": "Invalid credentials!"}), 401
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"message": "Server error!", "error": str(e)}), 500

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect("/login")

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all appointments
    cursor.execute("""
        SELECT a.id, a.time_slot, sc.id AS service_center_id, sc.center_name, sc.location, sc.rating 
        FROM appointments a 
        JOIN service_centers sc ON a.service_center_id = sc.id 
        WHERE a.user_id = %s
    """, (user_id,))
    appointments = cursor.fetchall()
    tz = pytz.timezone('Asia/Kolkata')  # Define timezone early
    for appt in appointments:
        logger.debug(f"Raw time_slot for appt {appt['id']}: {appt['time_slot']}")
        appt["time_slot"] = appt["time_slot"].replace(tzinfo=tz)  # Make time_slot timezone-aware
        appt["display_time_slot"] = appt["time_slot"].strftime("%Y-%m-%d %I:%M %p")  # For display

    # Send reminders for appointments within 24-48 hours
    now = datetime.now(tz)
    reminder_window_start = now
    reminder_window_end = now + timedelta(hours=48)
    cursor.execute("SELECT email FROM auth WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        logger.debug(f"Checking reminders for user {user_id} at {now}")
        logger.debug(f"Reminder window: {reminder_window_start} to {reminder_window_end}")
        for appt in appointments:
            appt_time = appt["time_slot"]  # Already timezone-aware
            reminder_key = f"reminder_sent_{appt['id']}"
            logger.debug(f"Appointment {appt['id']} scheduled for {appt_time}, reminder_sent: {session.get(reminder_key)}")
            if reminder_window_start <= appt_time <= reminder_window_end:
                if not session.get(reminder_key, False):
                    reminder_body = f"""
                    Dear {session.get('username', 'User')},

                    This is a reminder for your upcoming appointment:
                    - Service Center: {appt['center_name']}
                    - Location: {appt['location']}
                    - Date: {appt['display_time_slot'].split()[0]}
                    - Time: {appt['display_time_slot'].split()[1]} {appt['display_time_slot'].split()[2]}

                    See you soon!
                    """
                    logger.info(f"Attempting to send reminder for appointment {appt['id']} to {user['email']}")
                    if send_email(user["email"], "Appointment Reminder", reminder_body):
                        session[reminder_key] = True
                        logger.info(f"Reminder sent successfully for appointment {appt['id']} to {user['email']}")
                    else:
                        logger.error(f"Failed to send reminder for appointment {appt['id']} to {user['email']}")
            else:
                logger.debug(f"Appointment {appt['id']} at {appt_time} outside reminder window")

        # Separate test email
        test_body = f"Test email sent at {now.strftime('%Y-%m-%d %H:%M:%S')} to verify SMTP."
        logger.info(f"Sending test email to {user['email']}")
        if not send_email(user["email"], "SMTP Test from Dashboard", test_body):
            logger.error(f"Test email failed to send to {user['email']}")

    cursor.execute("""
        SELECT r.id, r.rating AS user_rating, r.comment, sc.center_name, r.appointment_id 
        FROM reviews r 
        JOIN service_centers sc ON r.service_center_id = sc.id 
        WHERE r.user_id = %s
    """, (user_id,))
    reviews = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("dashboard.html", username=session["username"], appointments=appointments, reviews=reviews, now=now)  # Pass now as datetime

@app.route("/api/submit-review", methods=["POST"])
def submit_review():
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    user_id = session["user_id"]
    data = request.get_json()
    service_center_id = data.get("service_center_id")
    appointment_id = data.get("appointment_id")
    rating = data.get("rating")
    comment = data.get("comment", "")

    if not all([service_center_id, appointment_id, rating]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({"success": False, "error": "Rating must be between 1 and 5"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Invalid rating value"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if review already exists
    cursor.execute("SELECT id FROM reviews WHERE user_id = %s AND appointment_id = %s", (user_id, appointment_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "You have already submitted a review for this appointment"}), 400

    # Insert new review
    cursor.execute("""
        INSERT INTO reviews (user_id, service_center_id, appointment_id, rating, comment) 
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, service_center_id, appointment_id, rating, comment))

    # Update service center rating
    cursor.execute("""
        UPDATE service_centers 
        SET rating = (SELECT AVG(rating) FROM reviews WHERE service_center_id = %s) 
        WHERE id = %s
    """, (service_center_id, service_center_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Review submitted successfully"})

@app.route("/chatbot")
def chatbot():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect("/login")
    return render_template("chatbot.html")

@app.route("/api/chatbot", methods=["POST"])
def chatbot_api():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 403

    user_id = session["user_id"]
    username = session.get("username")
    data = request.get_json()
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"response": "Please enter a valid message."})

    # Use generate_response
    bot_response = generate_response(user_input, username, str(user_id))

    # Handle service center location flow
    last_message = session.get("last_bot_message", "")
    if "would you like help finding" in last_message.lower() or "would you like me to help you locate" in last_message.lower():
        if user_input.lower() in ["yes", "y"]:
            bot_response = "Please enter your location to find a nearby service center."
        else:
            bot_response = "Okay, let me know if you need further assistance."
    elif "please enter your location" in last_message.lower():
        service_centers = get_nearby_service_centers(user_input)
        if service_centers:
            session["service_centers"] = service_centers
            bot_response = "Please wait while I fetch the details. Redirecting you to the appointment page..."
            return jsonify({"response": bot_response, "redirect": "/appointment", "success": True})
        else:
            bot_response = "Sorry, no service centers found near your location."

    # Update last message in session
    session["last_bot_message"] = bot_response

    # Clear session state if not in location flow
    if "would you like" not in bot_response.lower() and "please enter your location" not in bot_response.lower():
        session.pop("last_bot_message", None)

    # Handle goodbye
    if any(word in user_input.lower() for word in ["bye", "goodbye", "see you later", "quit"]):
        return jsonify({"response": bot_response, "redirect": "/dashboard"})

    return jsonify({"response": bot_response})

@app.route("/appointment")
def appointment():
    if "user_id" not in session:
        flash("Please log in first!", "warning")
        return redirect("/login")
    service_centers = session.get("service_centers", [])
    if not service_centers:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, center_name, location, contact_number, rating FROM service_centers")
        service_centers = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template("appointment.html", service_centers=service_centers)

@app.route("/api/time-slots", methods=["GET"])
def get_time_slots():
    center_id = request.args.get("center_id")
    date = request.args.get("date", datetime.today().strftime("%Y-%m-%d"))
    if not center_id:
        return jsonify({"error": "Center ID is required"}), 400

    try:
        selected_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT time_slot 
        FROM appointments 
        WHERE service_center_id = %s 
        AND DATE(time_slot) = %s
    """, (center_id, selected_date))
    booked_slots = [row["time_slot"].strftime("%I:%M %p") for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    all_slots = generate_time_slots()
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)
    slots = [
        {
            "time": slot,
            "booked": slot in booked_slots or datetime.strptime(f"{date} {slot}", "%Y-%m-%d %I:%M %p").replace(tzinfo=tz) < current_time
        }
        for slot in all_slots
    ]
    return jsonify({"slots": slots, "date": date})

@app.route("/api/book-appointment", methods=["POST"])
def book_appointment():
    data = request.get_json()
    center_id = data.get("center_id")
    time = data.get("time")  # Expecting AM/PM format, e.g., "01:00 PM"
    user_id = data.get("user_id") or session.get("user_id")
    date = data.get("date")

    if not all([center_id, time, user_id, date]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        time_slot = datetime.strptime(f"{date} {time}", "%Y-%m-%d %I:%M %p").replace(tzinfo=tz)
        time_slot_24hr = time_slot.strftime("%Y-%m-%d %H:%M:%S")

        logger.debug(f"Current time: {now}, Booking time: {time_slot}")
        if time_slot < now:
            logger.warning(f"Time slot {time_slot} is in the past compared to {now}")
            return jsonify({"success": False, "error": "Cannot book a past time slot"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if slot is already booked
        cursor.execute("SELECT * FROM appointments WHERE service_center_id = %s AND time_slot = %s", (center_id, time_slot_24hr))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "error": "This time slot is already booked"}), 400

        # Insert appointment in 24-hour format
        cursor.execute("INSERT INTO appointments (user_id, service_center_id, time_slot) VALUES (%s, %s, %s)", 
                       (user_id, center_id, time_slot_24hr))
        conn.commit()

        # Fetch user and center details for email
        cursor.execute("SELECT email FROM auth WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.execute("SELECT center_name, location FROM service_centers WHERE id = %s", (center_id,))
        center = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user or not center:
            logger.error(f"User {user_id} or center {center_id} not found for email notification.")
            return jsonify({"success": True, "message": "Appointment booked, but email notification failed due to missing data"})

        # Send confirmation email
        email_body = f"""
        Dear {session.get('username', 'User')},

        Your appointment has been successfully booked!
        Details:
        - Service Center: {center['center_name']}
        - Location: {center['location']}
        - Date: {date}
        - Time: {time}

        Thank you for booking with us!
        """
        logger.info(f"Attempting to send booking confirmation to {user['email']}")
        if not send_email(user["email"], "Appointment Confirmation", email_body):
            logger.error(f"Booking email failed to send to {user['email']}")
            return jsonify({"success": True, "message": "Appointment booked, but email failed to send"})
        else:
            logger.info(f"Booking email sent successfully to {user['email']}")

        return jsonify({"success": True, "message": "Appointment booked successfully!"})

    except ValueError as e:
        logger.error(f"Time format error: {e}")
        return jsonify({"success": False, "error": "Invalid time format. Use HH:MM AM/PM (e.g., 02:00 PM)"}), 400
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error during booking email: {e}")
        return jsonify({"success": True, "message": "Appointment booked, but email failed to send"})
    except Exception as e:
        logger.error(f"Booking error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/logout")
def logout():
    if "user_id" in session:
        reset_chat_history(str(session["user_id"]))
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
