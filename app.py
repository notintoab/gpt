# flask --app app.py --debug run --port 8000

import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap5
from datetime import datetime

appdir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(appdir, 'gpt_main.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO']=True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    height = db.Column(db.Float)

    def __repr__(self):
        return f'<User {self.username}>'
    
class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    body_weight = db.Column(db.Float, nullable=False)
    muscle_weight = db.Column(db.Float, nullable=False)
    fat_weight = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Record {self.date_created} for user {self.user_id}>'
    
# route to index page
@app.route("/", methods=["GET", "POST"])
def index():
    # check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        results = Results.query.filter_by(user_id=user_id).all()
        user = User.query.get(user_id)
    else:
        results = []
        user = None
    
    return render_template(
        "index.html", 
        today_date=datetime.today().strftime('%d.%m.%Y'),
        user=user, results=results)

# route for login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for("index"))
        else:
            flash('Login failed, check your credentials.', 'danger')

    # render the login template and pass user=None
    return render_template("login.html", 
                           user=None, 
                           today_date=datetime.today().strftime('%d.%m.%Y'))

# route for signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        height = request.form['height']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists!', 'warning')
        else:
            new_user = User(username=username, 
                            email=email, 
                            password=password, 
                            height=height)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please login', 'success')
            return redirect(url_for("login"))

    # render the signup template and pass user=None
    return render_template("signup.html", 
                           user=None,
                           today_date=datetime.today().strftime('%d.%m.%Y'))

# route for logout
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for("index"))

# route for add record 
@app.route("/add", methods=("GET", "POST"))
def add_result():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']  # fetch the user_id from the session
    results = Results.query.filter_by(user_id=user_id).all()
    user = User.query.filter_by(id=user_id).first()
    
    if request.method == 'POST':
        date = request.form['date']
        date_created = datetime.strptime(date, '%Y-%m-%d')
        body_weight = float(request.form['body-weight'])
        muscle_weight = float(request.form['muscle-weight'])
        fat_weight = float(request.form['fat-weight'])
        result = Results(date_created=date_created,
                         body_weight=body_weight,
                         muscle_weight=muscle_weight,
                         fat_weight=fat_weight,
                         user_id=user_id)
        db.session.add(result)
        db.session.commit()
        return redirect(url_for("index"))

    return render_template(
        "add_form.html",
        today_date=datetime.today().strftime('%d.%m.%Y'),
        user=user,
        results=results       
    )

# route for edit record 
@app.route("/edit/<int:result_id>", methods=("GET", "POST"))
def edit_result(result_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user_id']  # fetch user_id from session
    result = Results.query.get_or_404(result_id)
    if result.user_id != user_id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))

    results = Results.query.filter_by(user_id=user_id).all()
    user = User.query.filter_by(id=user_id).first()
    
    if request.method == 'POST':
        date = request.form['date']
        date_created = datetime.strptime(date, '%Y-%m-%d')
        result.date_created = date_created
        result.body_weight = float(request.form['body-weight'])
        result.muscle_weight = float(request.form['muscle-weight'])
        result.fat_weight = float(request.form['fat-weight'])
        db.session.commit()
        return redirect(url_for("index"))

    return render_template(
        "edit_form.html",
        today_date=datetime.today().strftime('%d.%m.%Y'),
        user=user,
        results=results,
        result=result       
    )

# route for remove record 
@app.post("/remove/<int:result_id>")
def remove_result(result_id):
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']  # fetch user_id from session
    result = Results.query.get_or_404(result_id)
    if result.user_id != user_id:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))
    
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('index'))

# route for api 
@app.route('/api/data')
def get_data():

    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    
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

if __name__ == '__main__':
    app.run(port=8000, debug=True)