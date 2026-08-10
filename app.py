"""
app.py — Application Factory

MAD2 changes from MAD1:
  - Flask-Login replaced by flask-jwt-extended 
  - flask-cors for Vue frontend
  - Catch-all route added to serve Vue SPA (templates/index.html)
  - Error handlers return JSON instead of rendered HTML
"""

import time
from flask import Flask, jsonify, render_template, g

from config import Config
from models import db
from extensions import jwt, cors, cache, make_celery

from routes.auth    import auth_bp
from routes.admin   import admin_bp
from routes.company import company_bp
from routes.student import student_bp
from routes.api     import api_bp


def create_app():
    app = Flask(__name__)

    #config
    app.config.from_object(Config)

    #extensions
    db.init_app(app)
    jwt.init_app(app)

    # Same-origin -> Vue served by Flask on same host
    cors.init_app(app) #allows requests from any host/port
    cache.init_app(app)

    app.celery = make_celery(app) # stored on app, so tasks.py/celery_worker.py can use it

    @app.before_request
    def start_timer():
        g.start_time = time.perf_counter()

    @app.after_request
    def add_process_time_header(response):
        if hasattr(g, 'start_time'):
            diff = (time.perf_counter() - g.start_time) * 1000
            response.headers['X-Response-Time'] = f'{diff:.2f}ms'
        return response

    #blueprints (JSON API endpoints)
    app.register_blueprint(auth_bp)     # /api/auth/*
    app.register_blueprint(admin_bp)    # /api/admin/*
    app.register_blueprint(company_bp)  # /api/company/*
    app.register_blueprint(student_bp)  # /api/student/*
    app.register_blueprint(api_bp)      # /api/*

    @app.route('/cacheremove')
    def clear_cache():
        try:
            cache.clear()
            return jsonify({"msg": "Cache cleared successfully."}), 200
        except Exception as e:
            return jsonify({"msg": f"Failed to clear cache: {e}"}), 500

    # vue SPA entry point (all non-API, non-static routes serve -> index.html)
    # flask doesn't need separate routes cuz vue router handles actual navigation
    @app.route('/')
    @app.route('/<path:path>')
    def serve_vue(path=''):
        # skip catch-all for API and static routes
        if path.startswith('api/') or path.startswith('static/'):
            return jsonify({"msg": "Not found."}), 404
        return render_template('index.html')

    # Error handlers
    # a) JWT error handlers (return JSON, not HTML)
    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"msg": f"Missing token: {reason}"}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"msg": f"Invalid token: {reason}"}), 422

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has expired."}), 401

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has been revoked."}), 401

    # b) general error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"msg": "Forbidden — you do not have access to this resource."}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"msg": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"msg": "Internal server error."}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, threaded=True)