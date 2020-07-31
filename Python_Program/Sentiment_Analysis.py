import pickle
import os.path
import argparse

import CREDENTIALS as CREDENTIALS

from VoteClassifier import VoteClassifier

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

    # Definir los argumentos
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform", required=True,
       help="Platform from which the data will be obtained. Twitter = TW, Youtube = YT")
    ap.add_argument("--keyword", nargs='+',
       help="Keyword to listen tweets")
    ap.add_argument("--videoname", 
       help="Name of the video for which you want to get comments")

    # Object with the arguments
    args = ap.parse_args()

    # Check if the arguments were complete
    if (args.platform == 'TW'):

        # Chek that the keyword was received
        if(not args.keyword):
            print('\nWhen usign --plataform=TW you also need to send the --keyword parameter')
        
        else:
            # Start the tweets listener
            TWTweets.listenTweets(voteClassifier, args.keyword)

    # Check if the arguments were complete
    elif (args.platform == 'YT'):

        # Chek that the keyword was received
        if(not args.videoname):
            print('\nWhen usign --plataform=YT you also need to send the --videoname parameter')
        
        else:
            # Start the youtube comments analizer
            YTComments.getCommentsFromVideo(voteClassifier, args.videoname)
    
    else:
        print("The parameter --plataform muste be TW or YT")

