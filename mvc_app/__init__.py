import os

from flask import Flask, redirect, render_template, request, session, url_for
from flask_migrate import Migrate

from mvc_app.controllers import api_bp, web_bp
from mvc_app.models import db


migrate = Migrate()


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp)

    @app.before_request
    def require_login():
        allowed_endpoints = {
            'web.login',
            'web.register',
            'static',
            'api.health',
            'api.list_recipients',
            'api.create_recipient',
            'api.list_events',
            'api.create_event',
            'api.list_gifts',
            'api.create_gift',
        }
        if request.endpoint in allowed_endpoints:
            return None
        if request.endpoint is None:
            return None
        if 'user_id' not in session:
            return redirect(url_for('web.login'))
        return None

    @app.errorhandler(404)
    def page_not_found(_e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(_e):
        return render_template('500.html'), 500

    with app.app_context():
        db.create_all()

    return app
