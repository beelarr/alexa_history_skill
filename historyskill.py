# tracks events will help with debugging
import logging

# enables accessing operation system dependent functionality
import os

#regular expression matching operations
import re

#  creates compatibility across python 2 || 3
from six.moves.urllib.request import urlopen



from flask import Flask
from flask_ask import Ask, request, session, question, statement

# creates and instance of Flask and Ask
app = Flask(__name__)
ask = Ask(app, "/")

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# api url
URL_PREFIX = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&explaintext=&exsectionformat=plain&redirects=&titles='

# number of events to read at a given time
PAGINATION_SIZE = 3

# length of delimter between individual events
DELIMITER_SIZE = 2

# number of responses from wiki
SIZE_OF_EVENTS = 10

# defines session attribure key for event index
SESSION_INDEX = 'index'

# event text for event date
SESSION_TEXT = 'text'





