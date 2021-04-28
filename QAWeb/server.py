from flask import Flask
from flask_cors import CORS

from routes import routes

app = Flask(__name__, static_url_path='')
CORS(app, supports_credentials=True)
routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=8081)
    # app.run(host='0.0.0.0', port=80)