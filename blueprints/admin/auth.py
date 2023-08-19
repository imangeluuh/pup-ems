from flask import Blueprint, render_template, url_for, request, redirect

auth = Blueprint('auth', __name__, static_folder="static", template_folder="templates", static_url_path='static')

@auth.route('/login', methods=['GET', 'POST'])
def adminLogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password)
        return redirect(url_for('main.index'))
    return render_template('admin/admin_login.html')


@auth.route('/logout')
def logout():
    return "Use this to log out"