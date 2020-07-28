from bmc import bmc_app, db
from bmc.forms import LoginForm, RegistrationForm
from bmc.library import Library
from bmc.models import User
from flask import render_template, request
from flask import request, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

@bmc_app.route('/hello', methods = ['POST', 'GET'])
def index():
    name = request.args.get('name', 'Nobody')

    if (request.method == 'POST'):
        name = request.form['name']
        greet = request.form['greet']
        greeting = f'{greet}, {name}'
        return render_template("index.html", greeting = greeting)
    else:
        return render_template("hello_form.html")

def good_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bmc_app.route('/file', methods = ['POST', 'GET'])
@login_required
def potato():
    if (request.method == 'POST'):
        file = request.files['file']
        name = request.form['name']
        
        filename = secure_filename(name)

        if file and good_file(file.filename):
            file.save("images/" + filename + ".png")
            return render_template("uploaded.html")
    else:
        return render_template("file_upload.html")

@bmc_app.route('/bmc_start')
def enter():
    return render_template("bmc_books.html")

@bmc_app.route('/bmc_trial')
def memory():
    global book
    global library
    library = Library()
    try:
        book = request.args.get("book")
        return render_template('bmc_form.html', length = len(library.get(book)))
    except TypeError:
        return render_template('error.html')

@bmc_app.route('/bmc_final', methods = ['GET', 'POST'])
def result():
    if (request.method == 'POST'):
        correct = 0
        try:
            for x in range(0, len(library.get(book))):
                input = request.form[f"{x}"]
                if (input.lower() == library.get(book)[x].lower()):
                    correct += 1
            return render_template('bmc_result.html', result=correct)
        except TypeError:
            return render_template('error.html')
    else:
        return render_template('error.html')

@bmc_app.route('/login', methods = ['GET', 'POST'])
def login():
    if (current_user.is_authenticated):
        return redirect(url_for('potato'))
    form = LoginForm()
    if (form.validate_on_submit()):
        user = User.query.filter_by(username=form.username.data).first()
        if (user is None or not user.check_password(form.password.data)):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if (not next_page or url_parse(next_page).netloc != ''):
            next_page = url_for('potato')
        return redirect(next_page)
    return render_template('login.html', form = form)

@bmc_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('potato'))


@bmc_app.route('/')
@login_required
def hello():
    return render_template("hello_user.html")

@bmc_app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('potato'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you have been registered!")
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)