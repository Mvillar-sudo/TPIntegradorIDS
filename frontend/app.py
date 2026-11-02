import os
from dotenv import load_dotenv
from flask import Flask
from routes.recepcion import recepcion_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FRONTEND_SECRET_KEY', 'clave-solo-para-desarrollo')

app.register_blueprint(recepcion_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)