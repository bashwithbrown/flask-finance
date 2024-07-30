from flask import Flask, render_template
from flask_login import LoginManager

from core import config
from database import DatabaseManager

database_manager = DatabaseManager(config.DATABASE)


def create_app():
    app = Flask(__name__)
    
    app.config["SECRET_KEY"] = config.CREDENTIALS['SECRET_KEY']
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{config.DATABASE}"

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        with database_manager as session:
            user = session.query(database_manager.User).filter_by(id=user_id).first()
        return user

    from routes import auth, main, admin, api, user, finance
    
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(user, url_prefix='/user') 
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(finance, url_prefix='/finance')
    
    return app

