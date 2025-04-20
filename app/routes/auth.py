from flask import render_template, redirect, url_for, flash, Blueprint, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import (
    LoginForm, RegistrationForm, ChangePasswordForm,
    ResetPasswordForm
)
from app.models.user import User
from urllib.parse import urlparse
import os
from supabase import create_client, Client
import secrets
from datetime import datetime, timedelta
import traceback

auth_bp = Blueprint('auth', __name__)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/callback')
def callback():
    try:
        # Check for access token in URL fragment or query parameters
        access_token = request.args.get('access_token')
        code = request.args.get('code')
        
        if access_token:
            # Get user data directly using the access token
            auth_response = supabase.auth.get_user(access_token)
            user_data = auth_response.user
        elif code:
            # Exchange the code for a session
            auth_response = supabase.auth.exchange_code_for_session({
                'auth_code': code
            })
            user_data = auth_response.user
        else:
            flash('Authentication failed: No authentication credentials provided')
            return redirect(url_for('auth.login'))

        if user_data and user_data.email:
            email = user_data.email
            name = user_data.user_metadata.get('full_name', email.split('@')[0])
            
            # Check if user exists in your database
            user = User.get_by_email(email)
            
            if not user:
                # Create new user if they don't exist
                username = name.lower().replace(' ', '_')  # Create username from full name
                user = User.create_user(
                    username=username,
                    email=email,
                    password=secrets.token_urlsafe(32),  # Generate a random password
                    subscription_type='basic'
                )
            
            if user:
                # Log the user in
                login_user(user, remember=True)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('main.dashboard'))
        
        flash('Authentication failed')
        return redirect(url_for('auth.login'))
    
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        flash('Error during authentication. Please try again.')
        return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route accessed")
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            print(f"Attempting to register user: {form.username.data}, {form.email.data}")
            
            # Check if user already exists
            existing_user = User.get_by_email(form.email.data)
            if existing_user:
                flash('Email address already registered. Please use a different email.', 'error')
                return render_template('auth/register.html', form=form)
            
            # Create new user
            user = User.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                subscription_type=form.subscription_type.data
            )
            
            if user:
                print(f"User created successfully: {user.username}")
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                print("User creation failed")
                flash('Registration failed. Please try again.', 'error')
        except Exception as e:
            print(f"Registration error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('Registration failed. Please try again.', 'error')
    elif request.method == 'POST':
        print(f"Form validation errors: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/cancel-premium', methods=['GET'])
@login_required
def cancel_premium():
    try:
        print(f"Attempting to cancel premium for user {current_user.id}")
        if current_user.update_subscription('basic'):
            print("Cancellation successful")
            flash('Your premium subscription has been cancelled.', 'success')
            return redirect(url_for('main.dashboard'))
        
        print("Cancellation failed")
        flash('Failed to cancel subscription. Please try again.', 'error')
    except Exception as e:
        print(f"Error in cancel_premium: {str(e)}")
        print(f"Full error traceback: {traceback.format_exc()}")
        flash('An error occurred while cancelling your subscription.', 'error')
    
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/upgrade-premium', methods=['GET'])
@login_required
def upgrade_premium():
    try:
        print(f"Attempting to upgrade user {current_user.id} to premium")
        if current_user.update_subscription('premium'):
            print("Upgrade successful")
            flash('Successfully upgraded to Premium! You now have access to all premium features.', 'success')
            return redirect(url_for('main.dashboard'))
        
        print("Upgrade failed")
        flash('Failed to upgrade subscription. Please try again.', 'error')
    except Exception as e:
        print(f"Error in upgrade_premium: {str(e)}")
        print(f"Full error traceback: {traceback.format_exc()}")
        flash('An error occurred while upgrading your subscription.', 'error')
    
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.get_by_id(current_user.id)
        if user and user.check_password(form.current_password.data):
            try:
                response = supabase.table('user').update(
                    {"password_hash": generate_password_hash(form.new_password.data)}
                ).eq("id", current_user.id).execute()
                
                if response.data:
                    flash('Your password has been updated!', 'success')
                    return redirect(url_for('main.dashboard'))
                
                flash('Failed to update password. Please try again.', 'error')
            except Exception as e:
                flash(f'Failed to update password: {str(e)}', 'error')
        else:
            flash('Current password is incorrect.', 'error')
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user:
            try:
                # Update password in database
                hashed_password = generate_password_hash(form.password.data)
                response = supabase.table('user').update(
                    {"password_hash": hashed_password}
                ).eq("id", user.id).execute()
                
                if response.data:
                    flash('Your password has been updated! You can now log in with your new password.', 'success')
                    return redirect(url_for('auth.login'))
                
                flash('Failed to update password. Please try again.', 'error')
            except Exception as e:
                print(f"Error updating password: {str(e)}")
                flash('An error occurred. Please try again.', 'error')
        else:
            flash('No account found with that email address.', 'error')
        
        return redirect(url_for('auth.reset_password'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form) 