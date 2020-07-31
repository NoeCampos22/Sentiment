import pickle
import os.path

# Imports the file with the credentials
import CREDENTIALS as CREDENTIALS

# Import the VoteClassifier class
from VoteClassifier import VoteClassifier

# Import the files to extract the youtube comments and tweets
import CommentsYoutube as YTComments
import GettingTweets as TWTweets


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
    wordFeatures = loadPickleFile(os.path.abspath(
        "pickleFiles/wordFeatures5k.pickle"))

    # Load the original naive bayes
    classifier = loadPickleFile(os.path.abspath(
        "pickleFiles/originalnaivebayes5k.pickle"))
    # Load the multinomial naive bayes
    MNB_classifier = loadPickleFile(os.path.abspath(
        "pickleFiles/MNB_classifier5k.pickle"))
    # Load the bernoulli naive bayes
    BernoulliNB_classifier = loadPickleFile(os.path.abspath(
        "pickleFiles/BernoulliNB_classifier5k.pickle"))
    # Load the bernoulli naive bayes
    LogisticRegression_classifier = loadPickleFile(os.path.abspath(
        "pickleFiles/LogisticRegression_classifier5k.pickle"))
    # Load the linear svc
    LinearSVC_classifier = loadPickleFile(os.path.abspath(
        "pickleFiles/LinearSVC_classifier5k.pickle"))

    # Build the Vote Classifier
    votedClassifier = VoteClassifier(classifier, MNB_classifier, BernoulliNB_classifier,
                                     LogisticRegression_classifier, LinearSVC_classifier, wordFeatures=wordFeatures)

    return votedClassifier


if __name__ == '__main__':
    voteClassifier = buildVoteClassifier()

    TWTweets.listenTweets(voteClassifier)

