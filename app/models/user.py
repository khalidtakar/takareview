from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import supabase
from datetime import datetime
from time import time
import jwt
from flask import current_app
from dateutil import parser
import traceback

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, subscription_type='basic', created_at=None, bio=None, profile_picture=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.subscription_type = subscription_type
        self.created_at = created_at
        self.bio = bio
        self.profile_picture = profile_picture

    @staticmethod
    def get_by_email(email):
        try:
            print(f"Attempting to get user by email: {email}")
            response = supabase.table('user').select("*").eq("email", email).execute()
            print(f"Response from get_by_email: {response.data}")
            
            if response.data and len(response.data) > 0:
                user_data = response.data[0]
                try:
                    created_at = parser.parse(user_data['created_at']) if user_data.get('created_at') else datetime.now()
                except (ValueError, TypeError):
                    created_at = datetime.now()
                
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    subscription_type=user_data.get('subscription_type', 'basic'),
                    created_at=created_at,
                    bio=user_data.get('bio'),
                    profile_picture=user_data.get('profile_picture')
                )
            return None
        except Exception as e:
            print(f"Error getting user by email: {str(e)}")
            traceback.print_exc()
            return None

    @staticmethod
    def create_user(username, email, password, subscription_type='basic'):
        try:
            print(f"Attempting to create user: {username}, {email}")
            
            # Check if user already exists
            existing_user = User.get_by_email(email)
            if existing_user:
                print(f"User with email {email} already exists")
                return None

            # Create new user data
            new_user_data = {
                'username': username,
                'email': email,
                'password_hash': generate_password_hash(password),
                'subscription_type': subscription_type,
                'created_at': datetime.now().isoformat()
            }
            
            print(f"Inserting new user data: {new_user_data}")
            
            # Insert into database
            response = supabase.table('user').insert(new_user_data).execute()
            print(f"Response from create_user: {response.data}")

            if response.data and len(response.data) > 0:
                user_data = response.data[0]
                try:
                    created_at = parser.parse(user_data['created_at'])
                except (ValueError, TypeError):
                    created_at = datetime.now()
                
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    subscription_type=user_data['subscription_type'],
                    created_at=created_at,
                    bio=user_data.get('bio'),
                    profile_picture=user_data.get('profile_picture')
                )
            return None
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            traceback.print_exc()
            return None

    @staticmethod
    def get_by_id(user_id):
        try:
            print(f"Attempting to get user by ID: {user_id}")
            
            # Convert string to integer if needed
            if isinstance(user_id, str):
                try:
                    user_id = int(user_id)
                except ValueError:
                    print(f"Invalid ID format: {user_id}")
                    return None

            response = supabase.table('user').select('*').eq('id', user_id).execute()
            print(f"Response from get_by_id: {response.data}")
            
            if response.data and len(response.data) > 0:
                user_data = response.data[0]
                try:
                    created_at = parser.parse(user_data['created_at']) if user_data.get('created_at') else datetime.now()
                except (ValueError, TypeError):
                    created_at = datetime.now()
                
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password_hash'],
                    subscription_type=user_data.get('subscription_type', 'basic'),
                    created_at=created_at,
                    bio=user_data.get('bio'),
                    profile_picture=user_data.get('profile_picture')
                )
            return None
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            traceback.print_exc()
            return None

    def check_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            print(f"Error checking password: {str(e)}")
            traceback.print_exc()
            return False

    def get_id(self):
        return str(self.id)  # Convert ID to string for Flask-Login

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_reset_password_token(self, expires_in=3600):
        try:
            return jwt.encode(
                {'reset_password': self.id, 'exp': time() + expires_in},
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            print(f"Error generating reset token: {str(e)}")
            traceback.print_exc()
            return None

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                           algorithms=['HS256'])['reset_password']
            return User.get_by_id(id)
        except Exception as e:
            print(f"Error verifying reset token: {str(e)}")
            traceback.print_exc()
            return None

    def update_profile(self, profile_picture=None, bio=None):
        try:
            print(f"Attempting to update profile for user {self.id}")
            update_data = {}
            if profile_picture is not None:
                update_data['profile_picture'] = profile_picture
            if bio is not None:
                update_data['bio'] = bio

            if update_data:
                response = supabase.table('user').update(update_data).eq('id', self.id).execute()
                print(f"Response from update_profile: {response.data}")
                
                if response.data and len(response.data) > 0:
                    user_data = response.data[0]
                    self.profile_picture = user_data.get('profile_picture', self.profile_picture)
                    self.bio = user_data.get('bio', self.bio)
                    return True
            return False
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            traceback.print_exc()
            return False

    def update_subscription(self, new_type):
        try:
            print(f"Updating subscription for user {self.id} to {new_type}")
            response = supabase.table('user').update(
                {"subscription_type": new_type}
            ).eq("id", self.id).execute()
            
            print(f"Update subscription response: {response}")
            
            if response.data and len(response.data) > 0:
                self.subscription_type = new_type
                print(f"Successfully updated subscription to {new_type}")
                return True
            
            print("Failed to update subscription - no response data")
            return False
        except Exception as e:
            print(f"Error updating subscription: {str(e)}")
            traceback.print_exc()
            return False 