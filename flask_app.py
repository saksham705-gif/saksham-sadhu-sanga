import os, datetime
from flask import Flask, render_template, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config['JWT_SECRET_KEY'] = 'devotee-portal-2026'

# DATABASE CONNECTION
MONGO_URI = "mongodb+srv://admin:krishna123@cluster0.zescgny.mongodb.net/devotee_db?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client.devotee_db
jwt = JWTManager(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if db.users.find_one({"email": data.get('email')}):
        return jsonify({"msg": "User already exists"}), 400
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    db.users.insert_one({
        "fullName": data.get('fullName'),
        "email": data.get('email'),
        "password": hashed_pw,
        "created_at": datetime.datetime.utcnow()
    })
    return jsonify({"msg": "Success"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = db.users.find_one({"email": data.get('email')})
    if user and bcrypt.check_password_hash(user['password'], data.get('password')):
        token = create_access_token(identity=str(user['_id']))
        return jsonify(token=token, fullName=user.get('fullName', 'Devotee')), 200
    return jsonify({"msg": "Invalid email or password"}), 401

if __name__ == '__main__':
    app.run(debug=True)
