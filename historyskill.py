import logging

import random

# enables accessing operation system dependent functionality
import os

# regular expression matching operations
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
URL_PREFIX = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts' \
             '&format=json&explaintext=&exsectionformat=plain&redirects=&titles='

# number of events to read at a given time
PAGINATION_SIZE = 2

# length of delimiter between individual events
DELIMITER_SIZE = 2

# number of responses from wiki
SIZE_OF_EVENTS = 10

# defines session attribute key for event index
SESSION_INDEX = 'index'

# event text for event date
SESSION_TEXT = 'text'


@ask.launch
def launch():
    speech_output = 'History Scholar, What day do you want historical events for?'
    reprompt_text = "Using History Scholar, you can get historical events for any day of the year. " + \
                    "For example, you could say today, or December twentieth. " + \
                    " Which day do you want?"
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
        speech_output += " Wanna go deeper into history?"
        card_output += " Wanna go deeper into history?"
        reprompt_text = "Using History Scholar, you can get historical events for any day of the year. " + \
                        "For example, you could say today, or July first. " + \
                        "Which day do you want?"
        session.attributes[SESSION_INDEX] = PAGINATION_SIZE
        session.attributes[SESSION_TEXT] = events
        speech_output = '<speak>{}</speak>'.format(speech_output)
        # support for alexa cards in alexa app
        return question(speech_output).reprompt(reprompt_text).simple_card(card_title, card_output)


@ask.intent('GetNextEventIntent')
def get_next_event():
    events = session.attributes[SESSION_TEXT]
    index = session.attributes[SESSION_INDEX]
    card_title = "More events on this day in history"
    speech_output = ""
    card_output = ""
    i = 0
    while i < PAGINATION_SIZE and index < len(events):
        speech_output += "<p>{}</p>".format(events[index])
        card_output += "{}\n".format(events[index])
        i += 1
        index += 1
    speech_output += " Wanna go deeper into history?"
    reprompt_text = "Do you want to know more about what happened on this date?"
    session.attributes[SESSION_INDEX] = index
    speech_output = '<speak>{}</speak>'.format(speech_output)
    return question(speech_output).reprompt(reprompt_text).simple_card(card_title, card_output)


@ask.intent('AMAZON.StopIntent')
def stop():
    return statement("Goodbye, for now.")


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("Goodbye, for now")


@ask.session_ended
def session_ended():
    return "{}", 200


# builds url, opens, reads, decodes and sends that to parse method
def _get_json_events_from_wikipedia(month, date):
    url = "{}{}_{}".format(URL_PREFIX, month, date)
    data = urlopen(url).read().decode('utf-8')
    return _parse_json(data)


def _parse_json(text):
    events = []
    try:
        slice_start = text.index("\\nEvents\\n") + SIZE_OF_EVENTS
        slice_end = text.index("\\n\\n\\nBirths")
        text = text[slice_start:slice_end]
    except ValueError:
        return events
    start_index = end_index = 0
    done = False
    while not done:
        try:
            end_index = text.index('\\n', start_index + DELIMITER_SIZE)
            event_text = text[start_index:end_index]
            start_index = end_index + 2
        except ValueError:
            event_text = text[start_index:]
            done = True
        # replaces dashes in wiki return
        event_text = event_text.replace('\\u2013', '')
        # add comma after year so Alexa pauses re.sub is regex substitute, <0>
        event_text = re.sub('^\d+', r'\g<0>,', event_text)
        events.append(event_text)
    random.shuffle(events)
    return events

# https://stackoverflow.com/questions/419163/what-does-if-name-main-do
if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)