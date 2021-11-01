# IMPORTS
import logging
import socket
from functools import wraps
from flask_login.config import EXEMPT_METHODS
from flask import Flask, render_template, current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user


# LOGGING
# filter out events that do not contain the word SECURITY
class SecurityFilter(logging.Filter):
    def filter(self, record):
        return "SECURITY" in record.getMessage()


fh = logging.FileHandler('lottery.log', 'w')
# track and log events at WARNING level and above
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

logger = logging.getLogger('')
# logging messages are not passed to the handlers of other loggers
logger.propagate = False
logger.addHandler(fh)


# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LfaLQEdAAAAAN2TYZO3d53-59chlOiQlEnYk6qR"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LfaLQEdAAAAAKjqEtMbcXa_XCkkWzUuWCBnF7kg"

# initialise database
db = SQLAlchemy(app)


# DECORATORS
# custom login _required decorator
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            # log anonymous users invalid attempts
            logging.warning('SECURITY - Anonymous invalid access [%s]', request.remote_addr)
            # Redirect the user to an unauthorised notice!
            return current_app.login_manager.unauthorized() and render_template('errors/403.html')
        return func(*args, **kwargs)

    return decorated_view


# custom requires_roles decorator
def requires_roles(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            # anonymous user has no role, nothing done
            if not current_user.is_authenticated:
                return func(*args, **kwargs)
            elif current_user.role not in roles:
                # log invalid access attempts
                logging.warning('SECURITY - Unauthorised access attempt [%s, %s, %s, %s %s]',
                                current_user.id, current_user.firstname, current_user.lastname,
                                current_user.role, request.remote_addr)
                # Redirect the user to an unauthorised notice!
                return render_template('errors/403.html')
            return func(*args, **kwargs)
        return wrapped
    return wrapper


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('index.html')


# error pages view
@app.errorhandler(400)
def bad_request(error):
    logging.warning('SECURITY - Bad request [%s]', request.remote_addr)
    return render_template('errors/400.html'), 400


@app.errorhandler(403)
def page_forbidden(error):
    logging.warning('SECURITY - Forbidden [%s]', request.remote_addr)
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def page_not_found(error):
    logging.warning('SECURITY - Page not found [%s]', request.remote_addr)
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    logging.warning('SECURITY - Internal server error [%s]', request.remote_addr)
    return render_template('errors/500.html'), 500


@app.errorhandler(503)
def service_unavailable(error):
    logging.warning('SECURITY - Service unavailable [%s]', request.remote_addr)
    return render_template('errors/503.html'), 503


if __name__ == "__main__":
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from lottery.views import lottery_blueprint

    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(lottery_blueprint)

    app.run(host=my_host, port=free_port, debug=True)
