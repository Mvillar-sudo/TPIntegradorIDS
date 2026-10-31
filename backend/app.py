from flask import Flask
from routes.auth import auth_bp

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix="api/v1")


if __name__ == "__main__":
    app.run(port=8080, debug=True)
