from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from . import db, bcrypt
from .models import User, Results
from .forms import LoginForm, SignupForm, AddRecordForm, EditRecordForm
from flask_login import login_user, login_required, logout_user, current_user

bp = Blueprint('main', __name__)

# route to index page
@bp.route("/")
def index():
    # use flask_login 'current_user' to get the logged-in user
    if current_user.is_authenticated:
        user = current_user
        results = Results.query.filter_by(user_id=user.id).all()
    else:
        user = None
        results = []

    return render_template(
        "index.html", 
        user=user, 
        results=results
    )

# route for login
@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for("main.index"))
        else:
            flash('Login failed, check your credentials.', 'danger')

    return render_template("login.html", form=form)

# route for signup
@bp.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()  
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        height = form.height.data

        # check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'warning')
        else:
            new_user = User(username=username, email=email, password=password, height=height)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please login', 'success')
            return redirect(url_for("main.login"))
    else:
        flash('Form validation failed. Please check your inputs.', 'danger')

    return render_template("signup.html", form=form)

# route for logout
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

# route for add record 
@bp.route("/add", methods=["GET", "POST"])
@login_required
def add_result():
    form = AddRecordForm()
    if form.validate_on_submit():
        date_created = form.date.data
        body_weight = form.body_weight.data
        muscle_weight = form.muscle_weight.data
        fat_weight = form.fat_weight.data
        user_id = current_user.id

        result = Results(date_created=date_created,
                         body_weight=body_weight,
                         muscle_weight=muscle_weight,
                         fat_weight=fat_weight,
                         user_id=user_id)
        db.session.add(result)
        db.session.commit()
        flash('Record added successfully!', 'success')
        return redirect(url_for("main.index"))

    return render_template("add_form.html", form=form)

# route for edit record 
@bp.route("/edit/<int:result_id>", methods=["GET", "POST"])
@login_required
def edit_result(result_id):
    result = Results.query.get_or_404(result_id)
    if result.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    form = EditRecordForm(obj=result)  # pre-fill form with current result data
    if result.date_created:
        form.date.data = result.date_created.date()  
    if form.validate_on_submit():
        result.date_created = form.date.data
        result.body_weight = form.body_weight.data
        result.muscle_weight = form.muscle_weight.data
        result.fat_weight = form.fat_weight.data
        db.session.commit()
        flash('Record updated successfully!', 'success')
        return redirect(url_for("main.index"))

    return render_template("edit_form.html", form=form, result=result)

# route for remove record 
@bp.route("/remove/<int:result_id>", methods=["POST"])
@login_required
def remove_result(result_id):
    result = Results.query.get_or_404(result_id)
    if result.user_id != current_user.id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(result)
    db.session.commit()
    flash('Record deleted successfully!', 'success')
    return redirect(url_for('main.index'))

# route for api 
@bp.route("/api/data")
@login_required
def get_data():
    user_id = current_user.id

    # fetch the results for current user
    results = Results.query.filter_by(user_id=user_id).all()

    # prepare data for JSON response
    data = {
        "dates": [result.date_created.strftime('%Y-%m-%d') for result in results],
        "body_weight": [result.body_weight for result in results],
        "muscle_weight": [result.muscle_weight for result in results],
        "fat_weight": [result.fat_weight for result in results]
    }

    return jsonify(data)

# route for demo mode
@bp.route('/demo')
def demo_login():
    # query the demo user
    demo_user = User.query.filter_by(username='demo_user').first()

    if demo_user:
        # log in demo user
        login_user(demo_user)
        flash('You are now logged in as a demo user.', 'warning')
        return redirect(url_for('main.index'))

    # if the demo user doesn't exist, show an error
    flash('Demo user not found. Please contact support.', 'danger')
    return redirect(url_for('main.index'))