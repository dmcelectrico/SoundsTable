import telebot
import requests
import sys
import time
import string
import logger
from os import environ
import telebot.types as types
import argparse
import logging
import logger
import json
import unidecode
import random

LOG = logging.getLogger('LaVidaModerna_Bot')
DATA_JSON = 'LaVidaModerna/data.json'

TELEGRAM_INLINE_MAX_RESULTS = 48

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", help="Defines log verbosity",
                    choices=['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'], default='INFO')
parser.add_argument("-b", "--bucket", help="Bucket or url where audios are stored",
                    default='https://github.com/dmcelectrico/SoundsTable/raw/master/LaVidaModerna/')
parser.add_argument("TELEGRAM_API_TOKEN", type=str, help="Telegram API token given by @botfather.")
args = parser.parse_args()

numeric_level = getattr(logging, args.verbosity.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.verbosity)
for logger in LOG.handlers:
    logger.setLevel(numeric_level)

LOG.info('Starting up bot...')

b_data_json = open(DATA_JSON).read()
data_json = json.loads(b_data_json)
remove = string.punctuation + string.whitespace
sounds = data_json["sounds"]

# Build sound URLs based in the bucket and unique IDs for the responses
for sound in sounds:
    sound["filename"] = args.bucket + sound["filename"]
    sound["id"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

bot = telebot.TeleBot(args.TELEGRAM_API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    LOG.debug(message)
    cid = message.chat.id
    bot.send_message(cid,
                     "Este bot es inline. Teclea su nombre en una conversación/grupo y podras enviar un mensaje moderno.")


@bot.inline_handler(lambda query: query.query == '')
def query_empty(inline_query):
    LOG.debug(inline_query)
    r = []
    for sound in sounds:
        r.append(types.InlineQueryResultVoice(
            sound["id"], sound["filename"], sound["text"], caption=sound["text"]))
        if len(r) > TELEGRAM_INLINE_MAX_RESULTS:  # https://core.telegram.org/bots/api#answerinlinequery
            break
    bot.answer_inline_query(inline_query.id, r)


@bot.inline_handler(lambda query: query.query)
def query_text(inline_query):
    LOG.debug(inline_query)
    try:
        text = unidecode.unidecode(inline_query.query.translate(remove).lower())
        LOG.debug("Querying: " + text)
        r = []
        for sound in sounds:
            if text in sound["description"]:
                r.append(types.InlineQueryResultVoice(
                    sound["id"], sound["filename"], sound["text"], caption=sound["text"]))
            if len(r) > TELEGRAM_INLINE_MAX_RESULTS:
                break
        bot.answer_inline_query(inline_query.id, r, cache_time=5)
    except Exception as e:
        LOG.error("Query aborted" + e, e)


try:
    LOG.debug("Polling started")
    bot.polling(none_stop=True)
except requests.exceptions.ConnectionError as e:
    LOG.critical(str(e), e)
