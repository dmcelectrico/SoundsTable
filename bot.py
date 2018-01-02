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


LOG = logger.getLogger('LaVidaModerna_Bot')
DATA_JSON = 'LaVidaModerna/data.json'
REMOVE_CHARS = string.punctuation + string.whitespace
TELEGRAM_INLINE_MAX_RESULTS = 48

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", help="Defines log verbosity",
                    choices=['CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'], default='INFO')
parser.add_argument("-b", "--bucket", help="Bucket or url where audios are stored",
                    default='https://github.com/dmcelectrico/SoundsTable/raw/master/LaVidaModerna/')
parser.add_argument("--database", help="Database file location")
parser.add_argument("TELEGRAM_API_TOKEN", type=str, help="Telegram API token given by @botfather.")
args = parser.parse_args()

BUCKET = args.bucket
logger.setLogLevel(args.verbosity)

LOG.info('Starting up bot...')
database = persistence.SqLite(db_file=args.database)
# Build sound URLs based in the bucket and unique IDs for the responses
# for sound in sounds:
#    sound["filename"] = args.bucket + sound["filename"]
#    if id not in sound:
#        sound["id"] = ''.join(random.choices(string.digits, k=8))
#        LOG.debug("Generated ID for %s: %s",sound["filename"],sound["id"])

bot = telebot.TeleBot(args.TELEGRAM_API_TOKEN)


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
            if text in sound["tags"]: #FIXME: Improve search
                r.append(types.InlineQueryResultVoice(
                    sound["id"], BUCKET + sound["filename"], sound["text"], caption=sound["text"]))
            if len(r) > TELEGRAM_INLINE_MAX_RESULTS:
                break
        bot.answer_inline_query(inline_query.id, r, cache_time=5)
    except Exception as e:
        LOG.error("Query aborted" + e, e)


def synchronize_sounds():
    db_sounds = database.get_sounds()
    LOG.debug("Sounds in db (%d): %s", len(db_sounds), str(db_sounds))

    b_data_json = open(DATA_JSON).read()
    data_json = json.loads(b_data_json)

    json_sounds = data_json["sounds"]
    LOG.debug("Sounds in data.json (%d): %s", len(json_sounds), str(json_sounds))
    json_modified = False

    for jsound in json_sounds:
        if jsound not in db_sounds:
            jsound["id"] = ''.join(random.choices(string.digits, k=8))
            database.add_sound(jsound["id"], jsound["filename"], jsound["text"], jsound["tags"])
            json_modified = True

    for db_sound in db_sounds:
        if db_sound not in json_sounds:
            database.delete_sound(db_sound['id'])

    if json_modified:
        # Reload database and synchronize data.json file
        data_json["sounds"] = database.get_sounds()
        LOG.info("Updating %s file", DATA_JSON)
        with open(DATA_JSON, 'w') as file:
            json.dump(data_json, file, indent=2, ensure_ascii=False)

    return db_sounds


sounds = synchronize_sounds()

while True:
    try:
        sleep(1)
        LOG.debug("Polling started")
        code = bot.polling()
        LOG.debug(code)
    except requests.exceptions.ConnectionError as connection_error:
        LOG.error("ConnectionError: Cannot connect to server.")
        LOG.debug(connection_error)
    except requests.exceptions.ReadTimeout as read_timeout:
        LOG.error("ReadTimeout: Lost connection to the server.")
        LOG.debug(read_timeout)
    except Exception as e:
        LOG.critical(e)
        raise e
