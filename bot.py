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

LOG = logging.getLogger('LaVidaModerna_Bot')

parser = argparse.ArgumentParser()

parser.add_argument("-v", "--verbosity", help="Defines log verbosity", choices=['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'], default='INFO')
parser.add_argument("-b", "--bucket", help="Bucket or url where audios are stored", default='https://github.com/dmcelectrico/SoundsTable/raw/master/LaVidaModerna/')
parser.add_argument("TELEGRAM_API_TOKEN", type=str, help="Telegram API token given by @botfather.")


args = parser.parse_args()

numeric_level = getattr(logging, args.verbosity.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.verbosity )
for logger in LOG.handlers:
    logger.setLevel(numeric_level)

LOG.info("Starting up bot...")

bot = telebot.TeleBot(args.TELEGRAM_API_TOKEN)
remove = string.punctuation + string.whitespace
sounds = [[args.bucket+"aPijoSacao.mp3", "A pijo sacao",
           "A pijo sacao"]]


@bot.message_handler(commands=['start'])
def send_welcome(message):
    LOG.debug(message)
    cid = message.chat.id
    bot.send_message(cid,
                     "Este bot es inline. Teclea su nombre en una conversación/grupo y podras enviar un mensaje moderno.")
    #bot.send_message(cid,
    #                 "Creado por @elraro . Puedes mejorarme en la siguiente dirección: https://github.com/elraro/rajoyBot")

@bot.inline_handler(lambda query: query.query == '')
def query_empty(inline_query):
    LOG.debug(inline_query)
    r = []
    for i, sound in enumerate(sounds):
        r.append(types.InlineQueryResultVoice(str(i), sound[0], sound[1], voice_duration=7))
    bot.answer_inline_query(inline_query.id, r)

@bot.inline_handler(lambda query: query.query)
def query_text(inline_query):
    LOG.debug(inline_query)
    try:
        text = inline_query.query.translate(remove).lower()
        r = []
        for i, sound in enumerate(sounds):
            if text in sound[2]:
                r.append(types.InlineQueryResultVoice(str(i), sound[0], sound[1], voice_duration=7))
        bot.answer_inline_query(inline_query.id, r)
    except Exception as e:
        LOG.error(str(e),e)



try:
    LOG.debug("Polling started")
    bot.polling(none_stop=True)
except requests.exceptions.ConnectionError as e:
    LOG.critical(str(e),e)
