from flask import Flask
from .extensions import db
from config import Config
from flask_cors import CORS


from .User.views import user as user_blueprint
from .Project.views import project as project_blueprint


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    db.init_app(app)

    # 
    with app.app_context():
        db.create_all()
    
    # 

    app.register_blueprint(user_blueprint)
    app.register_blueprint(project_blueprint)

    return app
