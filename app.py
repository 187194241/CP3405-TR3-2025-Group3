from flask import Flask, jsonify, render_template, request
import sqlite3

app = Flask(__name__)

# Connect to the database
def get_db_connection():
    conn = sqlite3.connect('seating_system.db')
    conn.row_factory = sqlite3.Row  # This will allow us to return results as dictionaries
    return conn

# Home route, render the user list
@app.route('/')
def index():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()  # Get all users
    conn.close()
    return render_template('index.html', users=users)  # Pass the user list to the template

# API: Get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()  # Get all users
    conn.close()
    return jsonify([dict(user) for user in users])  # Return users in JSON format

# API: Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    new_user = request.get_json()  # Get the JSON data from the request
    name = new_user['name']
    role = new_user['role']

    conn = get_db_connection()
    conn.execute('INSERT INTO users (name, role) VALUES (?, ?)', (name, role))  # Insert the new user
    conn.commit()
    conn.close()

    return jsonify(new_user), 201  # Return the new user data with status code 201 (Created)

# API: Get all reservations
@app.route('/reservations', methods=['GET'])
def get_reservations():
    conn = get_db_connection()
    reservations = conn.execute('SELECT * FROM reservations').fetchall()  # Get all reservations
    conn.close()
    return jsonify([dict(reservation) for reservation in reservations])  # Return reservations in JSON format

# API: Create a new reservation
@app.route('/reservations', methods=['POST'])
def create_reservation():
    new_reservation = request.get_json()  # Get reservation data from the request
    user_id = new_reservation['user_id']
    seat_number = new_reservation['seat_number']

    conn = get_db_connection()
    conn.execute('INSERT INTO reservations (user_id, seat_number) VALUES (?, ?)', (user_id, seat_number))  # Insert the new reservation
    conn.commit()
    conn.close()

    return jsonify(new_reservation), 201  # Return the new reservation data with status code 201 (Created)

if __name__ == '__main__':
    app.run(debug=True)
