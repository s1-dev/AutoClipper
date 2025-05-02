import http.client
import httplib2
import os
import random
import sys
import time
import json

from utils.dateUtils import convertUtcToEpoch, getCurrentEpoch

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.client import Credentials
from oauth2client.tools import argparser, run_flow

OAUTH_CONFIG_PATH = "testOAuthConfig.json"

CLIENT_SECRETS_FILE = "client_secrets.json"

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def _verifyConfig() -> bool:
    oAuthCredentials = _attemptToLoadConfig()
    if oAuthCredentials != None:
        oAuthConfig = json.loads(oAuthCredentials.to_json())
        # Check if refresh is needed 
        # if so, check if possible. If not tell user to reauthenticate
        if _isRefreshNeeded(oAuthConfig):
            print("OAUTH refresh is needed")
            if _isRefreshPossible(oAuthConfig):
                return _attemptRefreshCredentials(oAuthCredentials, "testOAuthConfig.json")
            else:
                print("OAUTH refresh not possible")
                return False
        return True
    else:
        print("OAUTH credentials are null")
        return False

def _attemptToLoadConfig() -> Credentials :
    storage = Storage("testOAuthConfig.json")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        return None
    
    return credentials

def _isRefreshNeeded(oAuthConfig) -> bool:
    expirationTime = convertUtcToEpoch(oAuthConfig['token_expiry'])
    currentTime = getCurrentEpoch()

    return currentTime >= expirationTime

def _isRefreshPossible(oAuthConfig) -> bool:
    expirationTime = convertUtcToEpoch(oAuthConfig['token_expiry'])
    refreshTokenExpirationTime = expirationTime + int(oAuthConfig["token_response"]["refresh_token_expires_in"])
    currentTime = getCurrentEpoch()

    return currentTime < refreshTokenExpirationTime

def _attemptRefreshCredentials(oAuthCredentials, pathToConfig) -> bool:
    try:
        http = httplib2.Http()
        oAuthCredentials.refresh(http)
        with open(pathToConfig, "w") as f:
            f.write(oAuthCredentials.to_json())
        return True
    except Exception as e:
        print(f"Refresh failed: {e}")
        return False

def _runAuthenticationFlow(configOutputPath):
    flow = flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_UPLOAD_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE,
    )
    storage = Storage(configOutputPath)
    credentials = run_flow(flow, storage, flags=None) # Flags allow you to modify the setup workflow

    return build(
        YOUTUBE_API_SERVICE_NAME, 
        YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()),
    )

# Public functions

def isOAuthSetup():
    return _verifyConfig()

def verifyOAuthIsSetup():
    isConfigValid = _verifyConfig()

    if not isConfigValid:
        decision = input("Would you like to run an OAUTH setup? (y/Y) ")
        if decision.lower() == "y":
            _runAuthenticationFlow(OAUTH_CONFIG_PATH) # TODO allow them to specify?
           # _runSetupFlow()
    else:
        print("OAuth config is valid!")
