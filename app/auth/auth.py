from flask import Blueprint, render_template, url_for, request, redirect

auth_bp = Blueprint('auth', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@auth_bp.route('/login', methods=['GET', 'POST'])
def participantLogin():
    # form = LoginForm()

    # if request.method == "POST":
    #     if form.validate_on_submit():
    #         admin_to_login = Login(email=form.email.data,
    #                                 password=form.password.data)
        
    # My guess for getting data
    # db.Query.filter_by(email=Login.email)
    # return redirect(url_for('home'))

    # For inserting data?
    # db.session.add(admin_to_login)
    # db.session.commit()

    # if request.method == "POST":
    #     email = request.form.get('email')
    #     password = request.form.get('password')
    #     print(email, password)
    #     return redirect(url_for('main.index'))
    return render_template('auth/participant/parti_login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def participantSignup():
    # form = LoginForm()

    # if request.method == "POST":
    #     if form.validate_on_submit():
    #         admin_to_login = Login(email=form.email.data,
    #                                 password=form.password.data)
        
    # My guess for getting data
    # db.Query.filter_by(email=Login.email)
    # return redirect(url_for('home'))

    # For inserting data?
    # db.session.add(admin_to_login)
    # db.session.commit()

    # if request.method == "POST":
    #     email = request.form.get('email')
    #     password = request.form.get('password')
    #     print(email, password)
    #     return redirect(url_for('main.index'))
    return render_template('auth/participant/parti_signup.html')

@auth_bp.route('/logout')
def logout():
    return "Use this to log out"