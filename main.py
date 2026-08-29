from flask import Flask
from services.db import close_db_connection, init_db
from controllers.web_controller import web_bp
from controllers.auth_controller import auth_bp
from controllers.api_controller import api_bp
from controllers.ml_controller import ml_bp

app = Flask(__name__)

app.teardown_appcontext(close_db_connection)

app.register_blueprint(web_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)
app.register_blueprint(ml_bp)

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
