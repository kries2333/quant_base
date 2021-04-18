from flask import Flask

from routes import routes

app = Flask(__name__)
routes(app)

if __name__ == '__main__':
    # app.run(debug=True, port=8081)
    app.run(host='0.0.0.0', port=80)