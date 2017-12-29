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


@ask.launch
def launch():
    speech_output = 'What day do you want events for?'
    reprompt_text = "You can get historical events for any day of the year. " \
                   "For example, you could say today, or December twentieth." \
                   "Which day do you want?"
    return question(speech_output).reprompt(reprompt_text)


# converts day to date from utterances
@ask.intent('GetFirstEventIntent', convert={'day': 'date'})
def get_first_event(day):
    month_name = day.strftime('%B')
    day_number = day.day
    events = _get_json_events_from_wikipedia(month_name, day_number)
    if not events:
        speech_output = "There is a problem connecting to my brain at this time. Please try again later."
        return statement('<speak>{}</speak>'.format(speech_output))

    else:
        card_title = "Events on {} {}".format(month_name, day_number)
        speech_output = "<p>For {} {}</p>".format(month_name, day_number)
        card_output = ""
        for i in range(PAGINATION_SIZE):
            speech_output += "<p>{}</p>".format(events[i])
            card_output += "{}\n".format(events[i])
        speech_output += "Wanna go deeper into history?"
        card_output += "Wanna go deeper into history?"
        reprompt_text = "You can get historical events for any day of the year. " \
                        "For example, you could say today, or December twentieth." \
                        "Which day do you want?"
        session.attributes[SESSION_INDEX] = [PAGINATION_SIZE]
        session.attributes[SESSION_TEXT] = events
        speech_output = '<speak>{}</speack>',format(speech_output)
        # support for alexa cards in alexa app
        return question(speech_output).reprompt(reprompt_text).simple_card(card_title, card_output)





