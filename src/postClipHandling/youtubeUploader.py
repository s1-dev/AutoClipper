import http.client
import httplib2
import random
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from utils.fileUtils import FileUtils

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
  http.client.IncompleteRead, http.client.ImproperConnectionState,
  http.client.CannotSendRequest, http.client.CannotSendHeader,
  http.client.ResponseNotReady, http.client.BadStatusLine)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def _getAuthenticatedService(oAuthConfigFile):
    storage = Storage(oAuthConfigFile)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        raise Exception("OAUTH not setup...")
    
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def _initializeUpload(youtubeService, videoOptionsDict):
    tags = None
    if videoOptionsDict['keywords']:
        tags = videoOptionsDict['keywords'].split(",")
    body = dict(
        snippet=dict(
            title=videoOptionsDict['title'],
            description=videoOptionsDict['description'],
            tags=tags,
            categoryId=videoOptionsDict['categoryId'],
        ),
        status = dict(
            privacyStatus=videoOptionsDict['privacyStatus'],
        ),
    )

    # Call the API's videos.insert method to create and upload the video.
    insertRequest = youtubeService.videos().insert(
        part = ",".join(body.keys()),
        body = body,
        # This comment was taken from youtube docs:
        #
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body = MediaFileUpload(videoOptionsDict['file'], chunksize=-1, resumable=True),
    )
    _resumableUpload(insertRequest)

def _resumableUpload(insertRequest):
    response = None
    error = None
    retryCount = 0

    while response is None:
        try:
            print("Attempting upload...")
            status, response = insertRequest.next_chunk() # Iterate if we allow more than 1 chunk
            if response is not None:
                if 'id' in response:
                    print(f"Video id '{response['id']}' was successfully uploaded.")
                else:
                    exit("The upload failed with an unexpected response: %s" % response) # TODO allow for graceful failure here
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

    if error is not None: 
        print(error)
        retryCount += 1
        if retryCount > MAX_RETRIES:
            exit("Ran out of retry attempts...") # TODO end gracefully 

        maxSleepTime = 2 ** retryCount
        sleepSeconds = random.random() * maxSleepTime
        print(f"Sleeping {float(sleepSeconds)} seconds and then retrying...")
        time.sleep(sleepSeconds)

# Public functions 

def uploadYoutubeVideo(
    filePath: str,
    pathToOAuthConfig: str, 
    videoDetails: dict,
) -> bool:
    if not FileUtils.isValidFile(filePath):
        print("Given file path to upload is not a valid file.")
        return False

    youtubeService = _getAuthenticatedService(pathToOAuthConfig)

    videoArgs = {
        'file': filePath,
        'title': videoDetails["title"],
        'description': videoDetails["description"],
        'keywords': videoDetails["keywords"],
        'categoryId' : videoDetails["categoryId"],
        'privacyStatus': videoDetails["privacyStatus"],
    }
    
    try:
        _initializeUpload(youtubeService, videoArgs)
        return True
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return False
