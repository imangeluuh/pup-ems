from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, current_user
from ..models import Project, ExtensionProgram, Program, Registration, Agenda
import calendar
from datetime import datetime
from sqlalchemy import extract
from app import db

programs_bp = Blueprint('programs', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@programs_bp.route('/programs')
def programsList():
    extension_programs = ExtensionProgram.query.all()
    programs = Program.query.all()
    agendas = Agenda.query.all()
    return render_template('programs/programs.html', extension_programs=extension_programs, programs=programs, agendas=agendas)


@programs_bp.route('/projects/<int:program_id>', methods=['GET', 'POST'])
def projectsList(program_id):
    projects = Project.query.filter_by(ExtensionProgramId=program_id).all()
    return render_template('programs/projects_list.html', projects=projects)
    # if 'submit' in request.args:
    #     dict_filter_conditions = {} 

    #     filter_value = request.args.get('filter')  
    #     option_value = request.args.get('option') 
    #     if filter_value == "All":
    #         return render_template('programs/projects_list.html', projects=projects)
    #     elif filter_value == "Month":
    #         dict_month = dict((month, index) for index, month in enumerate(calendar.month_name) if month)
    #         # Convert the selected option to a month number (1 for January, 2 for February, etc.)
    #         int_month = dict_month[option_value]
    #         dict_filter_conditions['Month'] =  extract('month', Project.StartDate) == int_month
    #     elif filter_value == "ExtensionProgram":
    #         dict_filter_conditions['ExtensionProgram'] =  Project.ExtensionProgram.Name = option_value


    #     # Get the projects based on the selected filter and option
    #     filtered_projects = Project.query.filter(dict_filter_conditions.get(filter_value)).all()

    #     return render_template('programs/projects_list.html', projects=filtered_projects)

    

@programs_bp.route('/filters')
def filters():
    # Retrieve only the names from the program table
    extension_programs = ExtensionProgram.query.with_entities(ExtensionProgram.Name).all()
    programs = Program.query.with_entities(Program.ProgramName).all()

    # Convert the query result into a list of names
    list_extension_programs = [extension_program[0] for extension_program in extension_programs]
    list_programs = [program[0] for program in programs]

    # Get the current month
    current_month = datetime.now().month

    # Create a list of months from current month to December
    list_months = [calendar.month_name[i] for i in range(current_month, 13)]

    dict_filters = {
        'Extension Program': list_extension_programs,
        'Program': list_programs,
        'Month': list_months,
    }

    str_filter = request.args.get('filter')

    list_filter = dict_filters[str_filter]

    return render_template('programs/filters.html',list_filter=list_filter)


@programs_bp.route('/registration/<int:project_id>', methods=['GET', 'POST'])
def registration(project_id):
    project = Project.query.get_or_404(project_id)
    user_id = current_user.UserLogin[0].UserId if current_user.is_authenticated else None
    bool_is_registered = True if Registration.query.filter_by(ProjectId=project_id, UserId=user_id).first() else False
    print( project_id, user_id)
    if request.method == 'POST':
        registration_to_create = Registration(ProjectId = project_id,
                                            UserId=user_id)
        try:
            db.session.add(registration_to_create)
            db.session.commit()
            flash('Registration Successful!', category='success')
        except  Exception as e:
            flash('There was an issue during registration.', category='error')
            print('There was an issue during registration.', str(e))

        return redirect(url_for('programs.registration', project_id=project_id))
    return render_template("programs/project_reg.html", project=project, bool_is_registered=bool_is_registered)

