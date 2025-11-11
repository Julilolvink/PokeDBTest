from flask import Flask
from dotenv import load_dotenv

def create_app():
    load_dotenv()  # loads .env once at startup
    app = Flask(__name__)
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    return app
