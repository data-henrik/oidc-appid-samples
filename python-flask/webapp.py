# Most actions are protected by using IBM Cloud App ID as an OpenID Connect
# authorization provider. Data is stored in a Db2 Warehouse on Cloud database.
# The app is designed to be ready for multi-tenant use, but not all functionality
# has been implemented yet. Right now, single-tenant operations are assumed.
#
# For the database schema see the file database.sql
#
# Written by Henrik Loeser (data-henrik), hloeser@de.ibm.com
# (C) 2021 by IBM

import flask, os, json, datetime, decimal, re, requests, time

# for loading .env
from dotenv import load_dotenv

# Needed for decoding / encoding credentials
from base64 import b64encode

# everything Flask for this app
from flask import (Flask, jsonify, make_response, redirect,request,
		   render_template, url_for, Response, stream_with_context)
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata, ProviderMetadata

# load environment
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Set up content security policy, so that resources can be loaded and executed
# Could be slightly optimized for further security, e.g., by making scripts
# local and be more specific about script execution.

# Read the configuration and possible environment variables
# There are from local .env, provided through K8s secrets or
# through service bindings.
APPID_CLIENT_ID=None
APPID_OAUTH_SERVER_URL=None
APPID_SECRET=None
FULL_HOSTNAME=None

# Now, check for any overwritten environment settings. 

# AppID settings
APPID_CLIENT_ID=os.getenv("APPID_CLIENT_ID", APPID_CLIENT_ID)
APPID_OAUTH_SERVER_URL=os.getenv("APPID_OAUTH_SERVER_URL", APPID_OAUTH_SERVER_URL)
APPID_SECRET=os.getenv("APPID_SECRET", APPID_SECRET)

FULL_HOSTNAME=os.getenv("FULL_HOSTNAME")

# Update Flask configuration
#'SERVER_NAME': os.getenv("HOSTNAME"),
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
