from app.api import bp
from flask import jsonify, request, url_for
from app.models import User, Login
from app.api.errors import bad_request
from app import db

@bp.route('/users/<string:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'Email' not in data or 'Password' not in data:
        return bad_request('Must include email and password fields')
    if Login.query.filter_by(Email = data['Email']).first():
        return bad_request('Please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.header['location'] = url_for('api.get_user', id=user.UserId)
    return response

@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass
