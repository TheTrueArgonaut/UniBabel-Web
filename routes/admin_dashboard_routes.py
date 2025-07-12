"""
Admin Dashboard Routes - SRIMI Microservice
Single Responsibility: Dashboard page serving only
"""

from flask import Flask, render_template, redirect
from flask_login import login_required, current_user
from functools import wraps

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect('/admin/login')
        if not getattr(current_user, 'is_data_vampire_admin', False):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function

def register_admin_dashboard_routes(app: Flask) -> None:
    """Register dashboard page routes - under 40 lines"""
    
    @app.route('/admin/dashboard')
    @login_required
    @require_admin
    def admin_dashboard():
        """Show admin dashboard"""
        return render_template('admin_dashboard.html')
    
    @app.route('/admin/analytics')
    @login_required
    @require_admin
    def analytics_dashboard():
        """Show analytics dashboard"""
        return render_template('analytics_dashboard.html')
    
    @app.route('/admin/user-profiles')
    @login_required
    @require_admin
    def user_profiles_popup():
        """Show user profiles popup dashboard"""
        return render_template('user_profiles_popup.html')