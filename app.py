from flask import Flask, render_template, session, request, redirect, jsonify, url_for
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

#intialise the Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = os.getenv("SECRET_KEY")  # Use the secret key from environment variables

#connecting to the database
client = MongoClient(os.getenv("MONGODB_URI"))  # Use the MongoDB URI from environment variables
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['MyDatabase']  # Change 'MyDatabase' to your actual database name
users_collection = db['users']  # Change 'users' to your actual collection name
messages_collection = db['messages']  # Change 'messages' to your actual collection name

@app.route("/login", methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['pass']

    user = users_collection.find_one({'email': email})
    if user and user['pass'] == password:
        session['user'] = user['email']
        return jsonify({'status': 200, 'user_email': session['user']})
    else:
        return jsonify({'error': 'Invalid email or password'})

@app.route("/register", methods=['POST'])
def create_user():
    # Check if request contains all required fields
    if 'name' not in request.json or 'email' not in request.json or 'pass' not in request.json:
        return jsonify({'error': 'Incomplete fields in the request'}), 400

    new_user = {
        'name': request.json['name'],
        'email': request.json['email'],
        'pass': request.json['pass']
    }
    
    # Check if a user with the same email already exists
    existing_user = users_collection.find_one({'email': new_user['email']})
    
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400

    # Insert the new user into the database
    users_collection.insert_one(new_user)
    
    return jsonify({'status': 'User created successfully'})

@app.route("/send-message", methods=['POST'])
def send_message():
    # Check if request contains all required fields
    if 'full_name' not in request.json or 'email' not in request.json or 'subject' not in request.json or 'phone_number' not in request.json or 'message' not in request.json:
        return jsonify({'error': 'Incomplete fields in the request'}), 400

    new_message = {
        'full_name': request.json['full_name'],
        'email': request.json['email'],
        'subject': request.json['subject'],
        'phone_number': request.json['phone_number'],
        'message': request.json['message']
    }
    
    # Insert the new message into the database
    messages_collection.insert_one(new_message)
    
    return jsonify({'status': 'Message sent successfully'})


if __name__ == '__main__':
    app.run(debug=True)
