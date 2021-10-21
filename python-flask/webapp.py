# Sample app to demonstrate how to use IBM Cloud App ID as an OpenID Connect
# authentication provider. Some actions are protected and only accessible
# after authentication.
#
# Written by Henrik Loeser (data-henrik), hloeser@de.ibm.com
# (C) 2021 by IBM


import flask, os

# for loading .env
from dotenv import load_dotenv

# everything Flask for this app
from flask import (Flask, redirect, render_template, url_for)
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata, ProviderMetadata

# load environment
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Read the configuration from environment variables

# AppID settings
APPID_CLIENT_ID=os.getenv("APPID_CLIENT_ID")
APPID_OAUTH_SERVER_URL=os.getenv("APPID_OAUTH_SERVER_URL")
APPID_SECRET=os.getenv("APPID_SECRET")

FULL_HOSTNAME=os.getenv("FULL_HOSTNAME")

# Update Flask configuration
app.config.update({'OIDC_REDIRECT_URI': FULL_HOSTNAME+'/redirect_uri',
                  'SECRET_KEY': 'my_not_so_dirty_secret_key',
                  'PERMANENT_SESSION_LIFETIME': 1800, # session time in second (30 minutes)
                  'DEBUG': os.getenv("FLASK_DEBUG", False)})


# Configure access to App ID service for the OpenID Connect client
appID_clientinfo=ClientMetadata(client_id=APPID_CLIENT_ID,client_secret=APPID_SECRET)
appID_config = ProviderConfiguration(issuer=APPID_OAUTH_SERVER_URL,client_metadata=appID_clientinfo)

# Initialize OpenID Connect client
auth=OIDCAuthentication({'default': appID_config}, app)


# Index page, unprotected to display some general information
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', startpage=True)

# Official login URI, print
@app.route('/login')
@auth.oidc_auth('default')
def login():
    return redirect(url_for('profile'))

# Show the user profile if logged in
# Protected by OIDC
@app.route('/profile')
@auth.oidc_auth('default')
def profile():
    return render_template('profile.html',id=flask.session['id_token'])
    
# End the session by logging off
@app.route('/logout')
@auth.oidc_logout
def logout():
    return redirect(url_for('index'))

# Start the actual app
# Get the PORT from environment
port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0',port=int(port))
