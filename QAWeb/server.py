from flask import Flask

from QAWeb.routes import routes

app = Flask(__name__)
routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=8081)