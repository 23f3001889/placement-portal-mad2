from flask import Flask
from models import db, Admin, Company, Student

def create_app():
    app = Flask(__name__)

    # ── Config ──────────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = 'mad1-project'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads/resumes'

    db.init_app(app)

    from flask import redirect, url_for
    @app.route('/')
    def index():
        return '<h2>Placement Portal is running — DB initialized, next I will build routes</h2>'

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
