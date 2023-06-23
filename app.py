from flask import Flask, render_template, request, session, redirect, flash
from models import connect_db, db, User, Feedback, bcrypt
from forms import UserForm, FeedbackForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    connect_db(app)
    db.create_all()

 
@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, email, first_name, last_name)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect(f'/users/{user.username}')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username,password)
        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_user(username):
    if 'username' not in session or session['username'] != username:
        return redirect('/')
    user = User.query.get(username)
    feedbacks = user.feedbacks
    return render_template('user.html', user=user, feedbacks=feedbacks)


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in session or session['username'] != username:
        flash("You must be logged in to view that page.", "danger")
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback added!", "success")
        return redirect(f'/users/{username}')
    return render_template('feedback_add.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if 'username' not in session or session['username'] != feedback.username:
        flash("You don't have permission to do that!", "danger")
        return redirect('/')
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Feedback updated!", "success")
        return redirect(f'/users/{feedback.username}')
    return render_template('feedback_edit.html', form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if 'username' not in session or session['username'] != feedback.username:
        flash("You don't have permission to do that!", "danger")
        return redirect('/')
    db.session.delete(feedback)
    db.session.commit()
    flash("Feedback deleted!", "success")
    return redirect(f'/users/{feedback.username}')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' not in session or session['username'] != username:
        flash("You don't have permission to do that!", "danger")
        return redirect('/')
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    flash("User deleted!", "success")
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')