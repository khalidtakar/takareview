from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models.user import User
from app import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index')) 