from flask import Blueprint, jsonify, request
from .models import User
from .decorators import read_write_separation

main = Blueprint('main', __name__)

@main.route('/users', methods=['GET'])
@read_write_separation(read_only=True)
def get_users(session):
    users = session.query(User).all()
    return jsonify([{'id': user.id, 'username': user.username, 'email': user.email} for user in users])

@main.route('/users', methods=['POST'])
@read_write_separation(read_only=False)
def create_user(session):
    data = request.get_json()
    new_user = User(
        username=data.get('username'),
        email=data.get('email')
    )
    session.add(new_user)
    session.commit()
    return jsonify({'message': 'User created successfully'}) 