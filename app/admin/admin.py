from flask import Blueprint, render_template, url_for, request, redirect

admin_bp = Blueprint('admin', __name__, template_folder="templates", static_folder="static", static_url_path='static')

@admin_bp.route('/login', methods=['GET', 'POST'])
def adminLogin():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password)
        return redirect(url_for('main.index'))
    return render_template('admin/admin_login.html')


@admin_bp.route('/logout')
def logout():
    return "Use this to log out"