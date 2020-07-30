import nltk
import pickle
import random
from statistics import mode

from nltk.classify import ClassifierI
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.classify.scikitlearn import SklearnClassifier

"""
VoteClassifier
Description: Class to vote between classifiers when a sentence is received
"""


class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers, wordFeatures):
        """ 
        Constructor method that saves the received list 
        of classifier algorithms

        Parameters:
        - classifiers: All the classifiers objects
        - wordFeatures: Frequency Distribution object
        """
        self._classifiers = classifiers
        self._wordFeatures = wordFeatures
        
        # Instace the lemmatizer
        self._lemmatizer = WordNetLemmatizer()

    def findFeatures(self, document):
        """
        Function to use the words as features and
        get a dictionary to know which words from the 
        frequency distribution list appear on the current
        sentence
        """
        # Token and tag the sentence
        byWords = word_tokenize(document)
        taggedWords = nltk.pos_tag(byWords)

        # Check word for word to leave just the allowed type of words
        adjectFilter = list(
            filter(lambda word: word[1][0] in ["J"], taggedWords))
        verbFilter = list(
            filter(lambda word: word[1][0] in ["V"], taggedWords))

        # Apply lemmatizer to the words
        adjectFilter = list(map(lambda word: self._lemmatizer.lemmatize(
            word[0].lower(), pos="a"), adjectFilter))
        verbFilter = list(map(lambda word: self._lemmatizer.lemmatize(
            word[0].lower(), pos="v"), verbFilter))

        # Get the features dictionary
        features = {}
        for word in self._wordFeatures:
            features[word] = (word in byWords)

        return features

    def classify(self, features):
        """
        Method in charge of classifying with all the algorithms,
        saving their ouput and getting the mode as if it were a vote.

        Parameters:
        - features: All the features (words) from a sentence

        Returns:
        - Label ('pos'/'neg')
        - Confidence value (float)
        """
        votesList = []
        for classifier in self._classifiers:
            v = classifier.classify(features)
            votesList.append(v)

        choiceVotes = votesList.count(mode(votesList))
        confValue = choiceVotes / len(votesList)

        return mode(votesList), confValue

    def getSentiment(self, text):
        """
        Function to classify the received text with the voted classifier and returns
        the label and confidence of the classification

        Paramters:
        - text: The text to classify

        Returns:
        - Label ('pos'/'neg')
        - Confidence value (float)
        """
        textFeatures = self.findFeatures(text)
        return self.classify(textFeatures)
