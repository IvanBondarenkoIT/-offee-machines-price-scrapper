"""
Internationalization routes - language switching
"""
from flask import Blueprint, session, redirect, url_for, request
from flask_login import current_user

bp = Blueprint('i18n', __name__)

@bp.route('/setlang/<lang>')
def set_language(lang):
    """
    Set user's preferred language
    
    Args:
        lang: Language code (en, ru, ka)
    """
    # Validate language
    from web_app.config import Config
    if lang not in Config.LANGUAGES:
        lang = 'en'
    
    # Store in session
    session['language'] = lang
    session.permanent = True
    
    # Redirect back to previous page or dashboard
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    return redirect(url_for('auth.login'))

