from flask_login import LoginManager
from flask_cors import CORS
from .models import db, User
from .routes import main
from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "Mg4R2O7RhQw1l1si7j47A5FxEuU4vxKR2meTh1LXMeB8kQ2Xcz"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat_app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    CORS(app)
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
