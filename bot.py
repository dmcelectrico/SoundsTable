import telebot
import requests
import string
import telebot.types as types
import argparse
import logger
import json
import unidecode
import random
from time import sleep
import persistence
import os

LOG = logger.get_logger('LaVidaModerna_Bot')
REMOVE_CHARS = string.punctuation + string.whitespace
TELEGRAM_INLINE_MAX_RESULTS = 48

_ENV_TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
_ENV_TELEGRAM_USER_ALIAS = "TELEGRAM_USER_ALIAS"
_ENV_DATABASE_SQLITE = 'DATABASE_SQLITE'
_ENV_DATA_JSON = 'DATA_JSON'
_ENV_LOGGING_FILE = 'LOGFILE'


parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", help="Defines log verbosity",
                    choices=['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'], default='INFO')
parser.add_argument("-b", "--bucket", help="Bucket or url where audios are stored",
                    default='https://github.com/dmcelectrico/SoundsTable/raw/master/LaVidaModerna/')
parser.add_argument("--database", help="Database file location", default='db.sqlite')
parser.add_argument("--token", type=str, help="Telegram API token given by @botfather.")
parser.add_argument("--admin", type=str, help="Alias of the admin user.")
parser.add_argument("--data", type=str, help="Data JSON path.", default='data.json')
parser.add_argument("--logfile", type=str, help="Log to defined file.")

args = parser.parse_args()

BUCKET = args.bucket


try:
    args.logfile = os.environ[_ENV_LOGGING_FILE]
except KeyError:
    pass

if args.logfile:
    logger.add_file_handler(args.logfile, args.verbosity)

logger.set_log_level(args.verbosity)


try:
    args.token = os.environ[_ENV_TELEGRAM_BOT_TOKEN]
except KeyError as key_error:
    if not args.token:
        LOG.critical(
            'No telegram bot token provided. Please do so using --token argument or %s environment variable.',
            _ENV_TELEGRAM_BOT_TOKEN)
        exit(1)

try:
    args.admin = os.environ[_ENV_TELEGRAM_USER_ALIAS]
except KeyError as key_error:
    if not args.admin:
        LOG.warn(
            'No admin user specified. Please do so using --admin argument or %s environment variable.',
            _ENV_TELEGRAM_USER_ALIAS)

try:
    args.database = os.environ[_ENV_DATABASE_SQLITE]
except KeyError:
    pass

try:
    args.data = os.environ[_ENV_DATA_JSON]
except KeyError:
    pass

LOG.info('Starting up bot...')
database = persistence.SqLite(db_file=args.database)

bot = telebot.TeleBot(args.token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    LOG.debug(message)
    cid = message.chat.id
    bot.send_message(cid,
                     "Este bot es inline. Teclea su nombre en una conversación/grupo y podras enviar un mensaje "
                     "moderno.")


@bot.inline_handler(lambda query: query.query == '')
def query_empty(inline_query):
    LOG.debug(inline_query)
    r = []
    for sound in sounds:
        r.append(types.InlineQueryResultVoice(
            sound["id"], BUCKET + sound["filename"], sound["text"], caption=sound["text"]))
        if len(r) > TELEGRAM_INLINE_MAX_RESULTS:  # https://core.telegram.org/bots/api#answerinlinequery
            break
    bot.answer_inline_query(inline_query.id, r)


@bot.inline_handler(lambda query: query.query)
def query_text(inline_query):
    LOG.debug(inline_query)
    try:
        text = unidecode.unidecode(inline_query.query.translate(REMOVE_CHARS).lower())
        LOG.debug("Querying: " + text)
        r = []
        for sound in sounds:
            if text in sound["tags"]:  # FIXME: Improve search
                r.append(types.InlineQueryResultVoice(
                    sound["id"], BUCKET + sound["filename"], sound["text"], caption=sound["text"]))
            if len(r) > TELEGRAM_INLINE_MAX_RESULTS:
                break
        bot.answer_inline_query(inline_query.id, r, cache_time=5)
    except Exception as e:
        LOG.error("Query aborted" + e, e)


def synchronize_sounds():
    db_sounds = database.get_sounds()
    LOG.debug("Sounds in db (%d)", len(db_sounds))

    b_data_json = open(args.data).read()
    data_json = json.loads(b_data_json)

    json_sounds = data_json["sounds"]
    LOG.debug("Sounds in data.json (%d)", len(json_sounds))

    # Adding new sounds to db
    for jsound in json_sounds:
        query = database.get_sound(filename=jsound["filename"])
        if len(query) == 0:
            jsound["id"] = ''.join(random.choices(string.digits, k=8))
            database.add_sound(jsound["id"], jsound["filename"], jsound["text"], jsound["tags"])
        if len(query) > 1:
            LOG.warn("Possible duplicate: %s", str(query))

    # Removing deleted sounds form db
    db_sounds = database.get_sounds()
    for db_sound in list(db_sounds):
        found = None
        for jsound in json_sounds:
            if jsound["filename"] == db_sound["filename"]:
                found = jsound
                break
        if not found:
            database.delete_sound(db_sound)
            db_sounds.remove(db_sound)

    return db_sounds


sounds = synchronize_sounds()
LOG.info('Serving %i sounds.', len(sounds))

while True:
    try:
        sleep(1)
        LOG.debug("Polling started")
        bot.polling()
    except requests.exceptions.ConnectionError as connection_error:
        LOG.error("ConnectionError: Cannot connect to server.")
        LOG.debug(connection_error)
    except requests.exceptions.ReadTimeout as read_timeout:
        LOG.error("ReadTimeout: Lost connection to the server.")
        LOG.debug(read_timeout)
    except Exception as e:
        LOG.critical(e)
        raise e
