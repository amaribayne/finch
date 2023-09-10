from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    # Create a Flask application instance
    app = Flask(__name__)

    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'

    # Initialize the database instance with the app
    db.init_app(app)

    # Import the models module to set up database models
    from app import models

    # Initialize the database by creating all tables
    with app.app_context():
        db.create_all()

    # Import the routes module to set up application routes
    from app import routes

    # Register the blueprint for the routes
    app.register_blueprint(routes.bp)

    return app
