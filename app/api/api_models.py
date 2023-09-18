from flask_restx import fields
from app import api

role_model = api.model("Role", {
    "RoleId": fields.Integer,
    "RoleName": fields.String,
    # "Login": fields.Nested,
})

login_input_model = api.model("LoginInput", {
    "Email": fields.String,
    "Password": fields.String,
})

login_model = api.model("Login", {
    "LoginId": fields.String,
    "Email": fields.String,
    "Password": fields.String,
    "RoleId": fields.Integer
})

register_input_model = api.model("RegisterInput", {
    "Email": fields.String,
    "Password": fields.String,
    "FirstName": fields.String,
    "MiddleName": fields.String,
    "LastName": fields.String,
    "ContactDetails": fields.String,
    "Birthdate": fields.Date,
    "Gender": fields.String,
    "Address": fields.String,
    "SkillsInterest": fields.String,
})

admin_model = api.model("Admin", {
    "AdminId": fields.String,
    "FirstName": fields.String,
    "LastName": fields.String,
    # "AdminLogin": fields.Nested(login_model)
})

user_model = api.model("User", {
    "UserId": fields.String,
    "FirstName": fields.String,
    "MiddleName": fields.String,
    "LastName": fields.String,
    "ContactDetails": fields.String,
    "Birthdate": fields.Date,
    "Gender": fields.String,
    "Address": fields.String,
    # "UserLogin": fields.Nested(login_model)
})