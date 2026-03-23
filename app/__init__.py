from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from config import Config
from .models import db


def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    from .routes import bp

    app.register_blueprint(bp)
    return app
