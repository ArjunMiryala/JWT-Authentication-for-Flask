from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, get_jwt, get_jwt_identity, jwt_required, create_refresh_token

app = Flask(__name__) #created a flask web app

app.config['JWT_SECRET_KEY'] = 'a8f5f167f44f4964e6c998dee827110c' # Secret key for signing the JWTs #we can change it   #  This is where the JWT token is created and signed using your secret key 
app.config['JWT_TOKEN_LOCATION'] = ['Headers']#This line tells Flask-JWT-Extended where to look for the JWT token in incoming requests.
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Disable expiry for simplicity (can customize later) #for learning ## In real apps, you should set a duration like timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = False # disable expiry for refresh tokens # for learning 
app.config["JWT_BLACKLIST_ENABLED"] = True  # # Turn on blacklist feature you can “log out” users.
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access","refresh"]  # # Check both token types #	Tells Flask-JWT to reject access and refresh tokens if they’re blacklisted.

blacklist = set()       #set() is an unordered collection with no duplicate elements.

jwt = JWTManager(app) # This sets up Flask and tells JWT to use 'mysecretkey' to sign tokens

# users = {                                                       #fake data base but we can use real ones in real project
    #"arjun" : "password123",
    #"alice" : "alicehelo123"
# }

users  = {
"arjun": {"password": "Password123", "role":"admin"},
"alice" : {"password": "Password456", "role":"user"}

}

## The user types their username and password and sends it as a POST request to /login
@app.route('/login', methods = ['post'])  #Sets up a POST route at /login ##Only POST is allowed (we’re sending data, not retrieving) 
def login():    

    username = request.json.get('username') #Grabs the username and password from the client request
    password = request.json.get('password')


    user = users.get(username) #heck if the username exists in our fake database. It returns the user dictionary if found, or None if not.

    '''if username in users and users[username] == password:  #Checks if the user exists and if the password matches
        access_token = create_access_token(identity=username) # Creates a JWT with the user's identity inside (e.g., “arjun”)
        return jsonify(access_token = access_token) #Sends the token back as a JSON response # This sends the token back to the user in a JSON response.
    '''
    if user and user["password"] ==password: #If the username is valid and the password matches, proceed.
        additional_claims = {"role":user["role"]} # Creating a dictionary with extra info (claims) that we want to include in the JWT — here, it's the user’s role (e.g., "admin")
        access_token = create_access_token(identity=username,additional_claims=additional_claims) #access_token for normal routes
        refresh_token = create_refresh_token(identity=username)    #refresh_token for re-authenticating
        return jsonify(access_token = access_token, refresh_token = refresh_token)


    return jsonify(msg = "Invalid credentials"), 401 # If login fails, return an error with status 401 (Unauthorized)
 
#When your access token expires, the frontend sends the refresh token to /refresh, and gets a new access token — without asking the user to log in again.
@app.route('/refresh', methods = ['POST']) #frontend calls refresh function whenever the jwt is expires we do not call it and it is not automatic
@jwt_required(refresh=True) # Only accepts a refresh token — normal access tokens won't work here
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token = new_access_token)


# A protected route (requires valid JWT)
@app.route('/protected', methods = ['GET'])  #Defines a new route called /protected.
@jwt_required() #this decorator blocks access unless a valid JWT token is sent in the request headers.
def protected(): 
    current_user = get_jwt_identity() #Extracts the identity (username in our case) stored in the JWT
    return jsonify(message = f"Welcome back,{current_user}!") #Sends back a welcome message showing the logged-in user’s name.


# @app.route('/') # When you go to http://localhost:5000/ #This sets up a route (like a page). The / means it’s the homepage.

# def home():   # The function that runs when someone visits the homepage.
#    return jsonify(message = "JWT Auth is runnning!") #returns a JSON message #sends back a JSON response to the browser or API client. 

@app.route('/admin',methods=['GET'])
@jwt_required() #ensures only users with avalid token can access
def admin_area():
    claims = get_jwt() # access all the claims(like role) # grabs the payload (claims) inside the JWT, including your custom "role" field.
    if claims["role"] != "admin":
        return jsonify(msg = "You are not autherized to access this area"),403
    return jsonify(msg="Welcome to the admin area!")

@jwt.token_in_blocklist_loader # This callback function is triggered automatically by Flask-JWT-Extended
def check_if_token_in_blacklist(jwt_header, jwt_payload):  ## whenever a protected route is accessed. It checks if the token is blacklisted. 
    return jwt_payload["jti"] in blacklist #Each JWT has a jti (JWT ID) — a unique identifier. We store bad ones here.

@app.route("/logout", methods = ["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"] # grab the token ID
    blacklist.add(jti) # add it to the blacklist
    return jsonify(msg = "successfully logged out"),200 #Now, once a user logs out Their token’s jti is added to the blacklist # Any further request with that token gets rejected

@app.route("/logout/refresh", methods = ["POST"])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()["jti"]
    blacklist.add(jti)
    return jsonify(msg = "refresh token revoked"),200
if __name__ == '__main__':
    app.run(debug=True) # Starts the app in debug mode #Starts the server with live-reload (handy for development).