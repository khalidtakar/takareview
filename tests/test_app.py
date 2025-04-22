import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Supabase before importing app
mock_supabase = MagicMock()
mock_supabase.table.return_value.select.return_value.limit.return_value.execute.return_value = {'data': []}

with patch('app.database.get_supabase', return_value=mock_supabase):
    from app import create_app
import json
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_app_creation(app):
    """Test that the app is created correctly."""
    assert app is not None
    assert app.config['TESTING'] is True
    assert app.config['WTF_CSRF_ENABLED'] is False

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'TakaReview' in response.data

def test_static_css(client):
    """Test that CSS files are accessible."""
    response = client.get('/static/css/style.css')
    assert response.status_code == 200
    assert 'text/css' in response.headers['Content-Type']

def test_static_js(client):
    """Test that JavaScript files are accessible."""
    response = client.get('/static/js/main.js')
    assert response.status_code == 200
    assert 'application/javascript' in response.headers['Content-Type']

def test_static_images(client):
    """Test that image files are accessible."""
    response = client.get('/static/images/logo-blue.jpg')
    assert response.status_code == 200
    assert 'image/jpeg' in response.headers['Content-Type']


def test_base_template(client):
    """Test that the base template is accessible."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data
    assert b'<html' in response.data
    assert b'<head>' in response.data
    assert b'<body>' in response.data

def test_navigation_links(client):
    """Test that navigation links are present."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<nav' in response.data
    assert b'<a href' in response.data

def test_script_tags(client):
    """Test that script tags are present."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<script' in response.data
    assert b'src="/static/js/main.js"' in response.data

def test_style_tags(client):
    """Test that style tags are present."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<link rel="stylesheet"' in response.data
    assert b'href="/static/css/style.css"' in response.data

def test_error_handling(client):
    """Test that error handling is working."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
    assert b'Not Found' in response.data

def test_authenticated_routes_redirect(client):
    """Test that authenticated routes redirect to login."""
    protected_routes = [
        '/settings',
        '/profile',
        '/dashboard',
        '/chat',
        '/analyse',
        '/export',
        '/details',
        '/change-password'
    ]
    
    for route in protected_routes:
        response = client.get(route)
        assert response.status_code == 302
        assert '/login' in response.location

def test_auth_routes(client):
    """Test that auth routes are accessible."""
    auth_routes = [
        '/login',
        '/register',
        '/reset-password'
    ]
    
    for route in auth_routes:
        response = client.get(route)
        assert response.status_code == 200
        assert b'<form' in response.data

def test_logout_route(client):
    """Test that logout route redirects to login."""
    response = client.get('/logout')
    assert response.status_code == 302
    assert '/login' in response.location

def test_register_route(client):
    """Test that register route is accessible."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data
