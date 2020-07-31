import os
import json
import time

# Imports from the Tweepy API
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

# Imports the file with the credentials
import CREDENTIALS as CREDENTIALS

# Variable to store the pointer to the CSV file
OUTPUT_FILE = None
# Variable to know if the output file already exists or not
FILE_EXISTS = False
# Global variable to store the VoteClassifier object
CLASSIFIER = None
# Count how many tweets were mined
TWEETS_COUNT = 0
# Count how many tweets were rejected
REJECT_COUNT = 0

class MyStreamListener(StreamListener):
    """
    Class in charge of getting the tweets and proccess them
    """
    def on_error(self, status):
        # status 420 is a warning to stop doing this
        if status == 420:
            return False
        # Print the error status
        print(status)

    def on_data(self, data):
        # Get the global variables
        global FILE_EXISTS
        global OUTPUT_FILE
        global TWEETS_COUNT
        global REJECT_COUNT
        global CLASSIFIER

        try:
            # Loads the tweet object
            tweetParsed = json.loads(data)

            # This is because sometimes the API returns a Limit notices object
            # More info:
            # https://developer.twitter.com/en/docs/tweets/filter-realtime/overview/statuses-filter
            if 'id_str' in tweetParsed:

                # If the text has more than 140 chars, the full text is inside
                # the extended_tweet object.
                if hasattr(tweetParsed, 'extended_tweet'):
                    textTweet = tweetParsed['extended_tweet']['full_text']
                else:
                    textTweet = tweetParsed['text']

                # Get the sentiment and the confidence
                sentimentValue, confidenceValue = CLASSIFIER.getSentiment(textTweet)
                print('{} {} \n {} \n\n'.format(
                    sentimentValue, confidenceValue, textTweet))

                # If the confidence of the classification is higher than
                # 80% write the tweet text on the output file
                if (confidenceValue * 100) >= 80:
                    finalSentiment = sentimentValue + \
                        ' ' + str(confidenceValue)
                    OUTPUT_FILE.write(finalSentiment)
                    OUTPUT_FILE.write('\n' + textTweet + '\n\n')

                # Print a dot
                _printResult('.')

            return True

        except Exception as ex:
            REJECT_COUNT += 1
            print(ex)

        return True

def _printResult(cChar):
    """
    Function to print a point or a asteristic(error)
    """
    global TWEETS_COUNT

    # Increase the tweets counter
    TWEETS_COUNT += 1

    if TWEETS_COUNT % 35 == 0:
        print(cChar)
    else:
        print(cChar, end=' ')

def _Get_Authentication():
    """
    Get the authentication of the twitter app
    """

    # Validate the Credentials
    Auth = OAuthHandler(CREDENTIALS.CON_KEY,
                        CREDENTIALS.CON_KEY_SECRET)
    # Validate the Acces Tokens
    Auth.set_access_token(CREDENTIALS.ACC_TOKEN,
                          CREDENTIALS.ACC_TOKEN_SECRET)
    return Auth

def listenTweets(voteClassifier, keyWords=['happy', 'sad']):
    """
    Function to start reading tweets.

    Parameters:
    - keyWords: The list of keywords to listen from twitter
    - voteClassifier: The object with the vote classifier
    """
    # Get the global variables
    global FILE_EXISTS
    global OUTPUT_FILE
    global TWEETS_COUNT
    global REJECT_COUNT
    global CLASSIFIER
    
    try:
        # Start to the listen tweets
        Auth = _Get_Authentication()
        myStreamListener = MyStreamListener()
        myStream = Stream(Auth, myStreamListener)

        # Output filename
        outputFile = 'Tweets_Sentiment.txt'

        # Check if the CSV file already exits
        if os.path.exists(outputFile):
            FILE_EXISTS = True

        # Open the file where the tweets are going to be write
        OUTPUT_FILE = open(outputFile, 'a+', encoding='UTF-8', newline='')

        # Build the VoteClassifie
        CLASSIFIER = voteClassifier
        print('Here')

        print("\n>> Listening tweets")

        # Filter the tweets by language (spanish) and the keywords
        myStream.filter(languages=["en"], track=keyWords, stall_warnings=True)

    # To stop the program
    except KeyboardInterrupt:

        # Close the CSV File
        OUTPUT_FILE.close()

        print("\n\n>> Mining finished.")
        print("{} tweets were written on the {} file".format(
            str(TWEETS_COUNT - REJECT_COUNT), outputFile))

    # Catch the excepetion
    except Exception as err:
        print()
        print(err)