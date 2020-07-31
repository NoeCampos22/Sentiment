import os
import pandas as pd

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import CREDENTIALS


def __get_authenticated_service():
    """
    Function to get the authentication on the Youtube API
    """
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS.CLIENT_SECRETS_FILE, CREDENTIALS.SCOPES)

    credentials = flow.run_console()

    return build(CREDENTIALS.API_SERVICE_NAME, CREDENTIALS.API_VERSION,
                 credentials=credentials)

def getCommentsFromVideo(videoName):
    service = __get_authenticated_service()

    # Get the name from the wanted video
    query = 'Trabajos de mierda, consejos para la busqueda de trabajo'

    # Execute the query on youtube
    query_results = service.search().list(  # pylint: disable=no-member
        part='snippet', q=query,
        order='relevance', maxResults=1,
        type='video', relevanceLanguage='en',
        safeSearch='moderate',
    ).execute()

    # Get Video ID
    queryResult = query_results['items'][0]
    video_id = queryResult['id']['videoId']

    # Execute the query to get the comments from the video
    commentsResp = service.commentThreads().list(  # pylint: disable=no-member
        part = 'snippet', videoId = video_id,
        maxResults = 100, order = 'relevance',
        textFormat = 'plainText',
    ).execute()

    # Get the text from all the received comments
    listComments = []
    for item in commentsResp['items']:
        listComments.append(
            item['snippet']['topLevelComment']['snippet']['textDisplay'])
    
    return listComments