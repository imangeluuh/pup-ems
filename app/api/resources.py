from flask_restx import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, current_user
from ..models import *
from app import db
from .api_models import *

authorizations = {
    "jsonWebToken": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

ns = Namespace("api", authorizations=authorizations)

@ns.route('/roles')
class RoleApi(Resource):

    @ns.marshal_list_with(role_model)
    def get(self):
        return Role.query.all()  
    
@ns.route('/accounts')
class AccountsApi(Resource):
    @ns.marshal_list_with(login_model)
    def get(self):
        return Login.query.all()  


@ns.route('/login/admin')
class AdminLoginApi(Resource):
    
    @ns.expect(login_input_model)
    def post(self):
        attempted_user = Login.query.filter_by(Email=ns.payload['Email'], RoleId=1).first()
        if attempted_user and attempted_user.Status == 'Active': 
            if attempted_user.check_password_correction(attempted_password=ns.payload['Password']):
                return {'access_token': create_access_token(attempted_user.LoginId)}
            else:
                return {'error': 'The password you\'ve entered is incorrect.'}, 404
        else:
            return {'error': 'The email you entered isn\'t connected to an account.'}, 404
        
@ns.route('/login/beneficiary')
class BeneficiaryLoginApi(Resource):
    
    @ns.expect(login_input_model)
    def post(self):
        attempted_user = Login.query.filter_by(Email=ns.payload['Email'], RoleId=2).first()
        if attempted_user and attempted_user.Status == 'Active': 
            if attempted_user.check_password_correction(attempted_password=ns.payload['Password']):
                return {'access_token': create_access_token(attempted_user.LoginId)}
            else:
                return {'error': 'The password you\'ve entered is incorrect.'}, 404
        else:
            return {'error': 'The email you entered isn\'t connected to an account.'}, 404
        
@ns.route('/login/student')
class StudentLoginApi(Resource):
    
    @ns.expect(login_input_model)
    def post(self):
        attempted_user = Login.query.filter_by(Email=ns.payload['Email'], RoleId=3).first()
        print(attempted_user)
        if attempted_user and attempted_user.Status == 'Active': 
            if attempted_user.check_password_correction(attempted_password=ns.payload['Password']):
                return {'access_token': create_access_token(attempted_user.LoginId)}
            else:
                return {'error': 'The password you\'ve entered is incorrect.'}, 404
        else:
            return {'error': 'The email you entered isn\'t connected to an account.'}, 404

@ns.route('/admins')
class AdminListApi(Resource):
    @ns.marshal_list_with(admin_model)
    def get(self):
        return Admin.query.all()
    
@ns.route('/users')
class UsersListApi(Resource):
    @ns.marshal_list_with(user_model)
    def get(self):
        return User.query.all()