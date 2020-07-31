import os
import pandas as pd

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import CREDENTIALS

def __GetAuthenticatedService():
    """
    Function to get the authentication on the Youtube API
    """
    print('\n\nPlease enter the link and log in')
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS.CLIENT_SECRETS_FILE, CREDENTIALS.SCOPES)

    credentials = flow.run_console()

    return build(CREDENTIALS.API_SERVICE_NAME, CREDENTIALS.API_VERSION,
                 credentials=credentials)


def getCommentsFromVideo(videoName, voteClassifier):
    """
    Function to get comments from the video that receives as parameter
    """
    # Authenticate on the Youtube API
    service = __GetAuthenticatedService()

    # Execute the query on youtube
    queryResult = service.search().list(  # pylint: disable=no-member
        part='snippet', q=videoName,
        order='relevance', maxResults=1,
        type='video', relevanceLanguage='en',
        safeSearch='moderate',
    ).execute()

    # Get Video ID
    queryResult = queryResult['items'][0]
    videoID = queryResult['id']['videoId']

    # Execute the query to get the comments from the video
    commentsResp = service.commentThreads().list(  # pylint: disable=no-member
        part = 'snippet', videoId = videoID,
        maxResults = 100, order = 'relevance',
        textFormat = 'plainText',
    ).execute()

    # Get the text from all the received comments
    listComments = []
    for item in commentsResp['items']:
        listComments.append(
            item['snippet']['topLevelComment']['snippet']['textDisplay'])

    # Output filename
    outputFile = 'Comments_Sentiment.txt'

    # Open the file where the tweets are going to be write
    OUTPUT_FILE = open(outputFile, 'a+', encoding='UTF-8', newline='')

    # Get the sentiment for each comment and write them
    for comment in listComments:

        # Get the sentiment and the confidence
        sentimentValue, confidenceValue = voteClassifier.getSentiment(comment)
        print('{} {} \n {} \n\n'.format(
            sentimentValue, confidenceValue, comment))

        # If the confidence of the classification is higher than
        # 80% write the tweet text on the output file
        if (confidenceValue * 100) >= 80:
            
            finalSentiment = sentimentValue + ' ' + str(confidenceValue)

            OUTPUT_FILE.write(finalSentiment)
            OUTPUT_FILE.write('\n' + comment + '\n\n')

    OUTPUT_FILE.close()