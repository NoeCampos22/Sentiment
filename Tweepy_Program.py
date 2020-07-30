# Imports from the Tweepy API
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

# To check if the file exist
import os.path

# Import the VoteClassifier class
from VoteClassifier import VoteClassifier

# Imports the file with the Twitter App credentials
import Tw_Credentials

# Another imports to parse the json
import json
import time
import pickle

# Variable to store the pointer to the CSV file
OUTPUT_FILE = None
# Variable to know if the output file already exists or not
FILE_EXISTS = False
# Global variable to store the VoteClassifier object
CLASSIFIER = False
# Count how many tweets were mined
TWEETS_COUNT = 0
# Count how many tweets were rejected
REJECT_COUNT = 0


def printResult(cChar):
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


def Get_Authentication():
    """
    Get the authentication of the twitter app
    """

    # Validate the Credentials
    Auth = OAuthHandler(Tw_Credentials.CON_KEY,
                        Tw_Credentials.CON_KEY_SECRET)
    # Validate the Acces Tokens
    Auth.set_access_token(Tw_Credentials.ACC_TOKEN,
                          Tw_Credentials.ACC_TOKEN_SECRET)
    return Auth


def loadPickleFile(path):
    """
    Function that loads the file from the received path 
    and return it
    """
    pickleFile = open(os.path.abspath(path), "rb")
    object = pickle.load(pickleFile)
    pickleFile.close()

    return object


def buildVoteClassifier():
    """
    Function that loads all the models from the 
    .pickle files, build the VoteClassifier with them
    and return it.
    """
    # Load the word features
    wordFeatures = loadPickleFile("./pickleFiles/wordFeatures5k.pickle")

    # Load the original naive bayes
    classifier = loadPickleFile("./pickleFiles/originalnaivebayes5k.pickle")
    # Load the multinomial naive bayes
    MNB_classifier = loadPickleFile("./pickleFiles/MNB_classifier5k.pickle")
    # Load the bernoulli naive bayes
    BernoulliNB_classifier = loadPickleFile(
        "./pickleFiles/BernoulliNB_classifier5k.pickle")
    # Load the bernoulli naive bayes
    LogisticRegression_classifier = loadPickleFile(
        "./pickleFiles/LogisticRegression_classifier5k.pickle")
    # Load the linear svc
    LinearSVC_classifier = loadPickleFile(
        "./pickleFiles/LinearSVC_classifier5k.pickle")

    # Build the Vote Classifier
    votedClassifier = VoteClassifier(classifier, MNB_classifier, BernoulliNB_classifier,
                                     LogisticRegression_classifier, LinearSVC_classifier, wordFeatures=wordFeatures)

    return votedClassifier


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
        try:
            # Get the global variables
            global FILE_EXISTS
            global OUTPUT_FILE
            global TWEETS_COUNT
            global REJECT_COUNT

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
                sentimentValue, confidenceValue = CLASSIFIER.getSentiment(
                    textTweet)
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
                printResult('.')

            return True

        except Exception as ex:
            REJECT_COUNT += 1
            print(ex)

        return True


if __name__ == '__main__':
    # An array with the key phrases to filter the tweets
    keyWords = ['happy', 'sad']

    print("\n====== Running App ======")

    try:
        # Start to the listen tweets
        Auth = Get_Authentication()
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
        CLASSIFIER = buildVoteClassifier()

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
