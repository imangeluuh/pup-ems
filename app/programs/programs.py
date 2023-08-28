from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, current_user
from ..models import Project, ExtensionProgram, Program
import calendar
from datetime import datetime

programs_bp = Blueprint('programs', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@programs_bp.route('/programs')
def programsList():
    pass


@programs_bp.route('/projects', methods=['GET', 'POST'])
def projectsList():
    projects = Project.query.all()

    if request.method == 'POST':
        dict_filter_conditions = {}

        filter_value = request.form.get('filter')  
        option_value = request.form.get('option') 

        if filter_value == 'All':
            return render_template('programs/projects_list.html', projects=projects)
        elif not filter_value == "":
            dict_filter_conditions[filter_value] = option_value

        # Get the projects based on the selected filter and option
        filtered_projects = Project.query.filter(dict_filter_conditions.get(filter_value)).all()

    return render_template('programs/projects_list.html', projects=projects)

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


