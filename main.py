from flask import Flask

def create_app():
    

    app = Flask(__name__)

    app.config.from_prefixed_env()      #This will load up environmental variables from the .env file with prefix
    # default prefix is FLASK prefix
    return app