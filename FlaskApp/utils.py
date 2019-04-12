from flask import redirect, url_for, session
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or len(session['username']) == 0:
            return redirect(url_for('auth.auth'))
        return f(*args, **kwargs)
    return decorated_function
