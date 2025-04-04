from flask import Flask, jsonify


app = Flask(__name__) #created a flask app

@app.route('/') # When you go to http://localhost:5000/

def home():
    return jsonify(message = "Hello JWT World") #returns a JSON message

if __name__ == '__main__':
    app.run(debug=True) # Starts the app in debug mode