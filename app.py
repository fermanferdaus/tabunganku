from flask import Flask
from services.db import close_db_connection, init_db
from routes.ml_routes import ml_bp
from routes.api_routes import api_bp
from routes.web_routes import web_bp

app = Flask(__name__)

app.teardown_appcontext(close_db_connection)

app.register_blueprint(web_bp)
app.register_blueprint(ml_bp)
app.register_blueprint(api_bp)

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
