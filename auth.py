from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from models import db, User
from forms import RegistrationForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        is_first_user = User.query.first() is None
        role = 'admin' if is_first_user else 'user'
        
        user = User(username=form.username.data, role=role)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        session['user_id'] = user.id
        session['user_role'] = user.role
        flash('You are now logged in', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))