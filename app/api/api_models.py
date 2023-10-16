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

agenda_model = api.model("Agenda", {
    "AgendaId": fields.Integer,
    "AgendaName": fields.String,
})

registration_model = api.model("Registration", {
    "RegistrationId": fields.Integer,
    "RegistrationDate": fields.Date,
    "ProjectId": fields.Integer,
    "User": fields.Nested(user_model)
})

extension_project_model = api.model("ExtensionProject", {
    "ProjectId": fields.Integer,
    "Name": fields.String,
    "LeadProponent": fields.String,
    "ProjectType": fields.String,
    "Rationale": fields.String,
    "Objectives": fields.String,
    "StartDate": fields.Date,
    "NumberOfBeneficiaries": fields.Integer,
    "BeneficiariesClassifications": fields.String,
    "ProjectScope": fields.String,
    "ExtensionProgramId": fields.Integer,
    "Registration": fields.List(fields.Nested(registration_model))
})

program_model = api.model("Program", {
    "ProgramId": fields.Integer,
    "ProgramName": fields.String,
    "Abbreviation": fields.String
})

extension_program_model = api.model("ExtensionProgram", {
    "ExtensionProgramId": fields.Integer,
    "Name": fields.String,
    "DateApproved": fields.Date,
    "ImplementationDate": fields.Date,
    "Status": fields.String,
    "ImageUrl": fields.String,
    "ImageFileId": fields.String,
    "Agenda": fields.Nested(agenda_model),
    "Program": fields.Nested(program_model),
    "Projects": fields.List(fields.Nested(extension_project_model))
})